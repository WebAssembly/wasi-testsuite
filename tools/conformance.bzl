"""Rules for turning Buck-built wasm artifacts into WASI conformance tests.

The build target that produces a `.wasm` file should stay language-specific
(`cxx_binary`, `rust_binary`, `assemblyscript_binary`, ...). The generic
`wasi_test` macro adds the runtime dimension by pairing those artifacts with a
`WasiRuntimeInfo` provider and delegating execution to the existing
`wasi_test_runner`.

`wasi_manifest` captures runner and distribution metadata.
`wasi_test` targets pair a wasm artifact with a runtime and manifest.
`wasi_suite` groups those targets for `buck2 test` and distribution packaging.
"""

load("@prelude//decls:common.bzl", "buck")
load("@prelude//test:inject_test_run_info.bzl", "inject_test_run_info")
load(":runtime.bzl", "WasiRuntimeInfo")

WasiTestInfo = provider(
    doc = "Provider describing one WASI test for dist packaging.",
    fields = {
        "config": provider_field(Artifact | None, default = None),
        "dist_dir": provider_field(str | None, default = None),
        "fixture_dirs": provider_field(dict[str, Artifact], default = {}),
        "suite_name": provider_field(str),
        "test_name": provider_field(str),
        "wasm": provider_field(Artifact),
        "wasi_version": provider_field(str),
    },
)

WasiTestSuiteInfo = provider(
    doc = "Provider collecting WASI test metadata for dist packaging.",
    fields = {
        "tests": provider_field(list[WasiTestInfo]),
    },
)

def _default_dist_dir(wasi_version: str) -> str:
    package = package_name()
    if package.endswith("/" + wasi_version):
        package = package.removesuffix("/" + wasi_version)
    return "{}/testsuite/{}".format(package, wasi_version)

def wasi_manifest(
        name: str,
        version: str,
        dist_dir: str | None = None,
        labels: list[str] = []):
    """Create runner manifest and dist metadata."""
    return struct(
        dist_dir = dist_dir or _default_dist_dir(version),
        labels = labels,
        name = "{} [{}]".format(name, version),
        version = version,
    )

def _infer_test_name(wasm):
    if type(wasm) != type(""):
        fail("wasi_test: test_name is required when wasm is not a label string")
    if ":" not in wasm:
        fail("wasi_test: cannot infer test_name from '{}'; pass test_name explicitly".format(wasm))
    return wasm.rsplit(":", 1)[1]

def _single_output(dep, attr_name):
    outputs = dep[DefaultInfo].default_outputs
    if len(outputs) != 1:
        fail("{} must provide exactly one output, got {}".format(attr_name, len(outputs)))
    return outputs[0]

def _wasi_test_impl(ctx: AnalysisContext) -> list[Provider]:
    wasm = _single_output(ctx.attrs.wasm, "wasm")
    runtime_info = ctx.attrs.runtime[WasiRuntimeInfo]
    runtime = runtime_info.runtime
    exclude_filter = ctx.attrs.exclude_filter or runtime_info.exclude_filter

    cmd = cmd_args(ctx.attrs._runner[RunInfo])
    cmd.add("--wasm", wasm)
    cmd.add("--test-name", ctx.attrs.test_name)
    cmd.add("--suite-name", ctx.attrs.suite_name)
    cmd.add("--wasi-version", ctx.attrs.wasi_version)
    cmd.add("--adapter", runtime_info.adapter)

    if ctx.attrs.config:
        cmd.add("--config", ctx.attrs.config)

    for guest_name, host_dir in ctx.attrs.fixture_dirs.items():
        cmd.add("--fixture-dir", guest_name, host_dir)

    if exclude_filter:
        cmd.add("--exclude-filter", exclude_filter)

    test_env = {
        runtime_info.runtime_env_var: runtime[RunInfo].args,
    }

    if runtime[DefaultInfo].default_outputs:
        cmd.add(cmd_args(hidden = runtime[DefaultInfo].default_outputs))

    return inject_test_run_info(
        ctx,
        ExternalRunnerTestInfo(
            type = "custom",
            command = [cmd],
            env = test_env,
            labels = runtime_info.labels + ctx.attrs.labels,
        ),
    ) + [
        DefaultInfo(default_output = wasm),
        WasiTestInfo(
            config = ctx.attrs.config,
            dist_dir = ctx.attrs.suite_dist_dir,
            fixture_dirs = ctx.attrs.fixture_dirs,
            suite_name = ctx.attrs.suite_name,
            test_name = ctx.attrs.test_name,
            wasm = wasm,
            wasi_version = ctx.attrs.wasi_version,
        ),
    ]

_wasi_test_rule = rule(
    impl = _wasi_test_impl,
    attrs = {
        "wasm": attrs.dep(providers = [DefaultInfo]),
        "test_name": attrs.string(),
        "suite_name": attrs.string(),
        "wasi_version": attrs.string(),
        "runtime": attrs.dep(providers = [WasiRuntimeInfo]),
        "config": attrs.option(attrs.source(), default = None),
        "fixture_dirs": attrs.dict(
            key = attrs.string(),
            value = attrs.source(allow_directory = True),
            default = {},
        ),
        "exclude_filter": attrs.option(attrs.source(), default = None),
        "suite_dist_dir": attrs.option(attrs.string(), default = None),
        "_runner": attrs.exec_dep(
            default = "//tools:run_wasi_test",
            providers = [RunInfo],
        ),
    } | buck.labels_arg() | buck.inject_test_env_arg(),
)

def wasi_test(
        name: str,
        wasm,
        runtime,
        manifest,
        config = None,
        dist_dir: str | None = None,
        fixture_dirs = {},
        exclude_filter = None,
        test_name = None,
        labels = [],
        visibility = None):
    """Run one Buck-built wasm artifact against one WASI runtime.

    Args:
        name: Buck target name for this test/runtime cell, e.g. `lseek_wasmtime`.
        wasm: Target producing the `.wasm` artifact under test.
        runtime: Target providing `WasiRuntimeInfo`.
        manifest: Metadata returned by `wasi_manifest`.
        config: Optional runner JSON config for this test.
        dist_dir: Optional archive relative dist directory; derived from package and version by default.
        fixture_dirs: Mutable preopened directories staged for the runner.
        exclude_filter: Optional runner exclude filter overriding the runtime default.
        test_name: Optional runner/dist test name; inferred from `wasm` labels.
        labels: Extra Buck test labels appended to manifest labels.
        visibility: Optional Buck visibility.
    """
    kwargs = {}
    if visibility != None:
        kwargs["visibility"] = visibility

    _wasi_test_rule(
        name = name,
        wasm = wasm,
        runtime = runtime,
        suite_name = manifest.name,
        suite_dist_dir = dist_dir or manifest.dist_dir,
        wasi_version = manifest.version,
        test_name = test_name or _infer_test_name(wasm),
        config = config,
        fixture_dirs = fixture_dirs,
        exclude_filter = exclude_filter,
        labels = manifest.labels + labels,
        **kwargs
    )

def _wasi_test_suite_impl(ctx: AnalysisContext) -> list[Provider]:
    tests = []
    test_targets = []
    other_outputs = []

    for test in ctx.attrs.test_deps:
        # Mirror test_suite shape so buck2 test traverses this target.
        test_targets.append(test.label.raw_target())
        default_info = test[DefaultInfo]
        other_outputs.extend(default_info.default_outputs)
        other_outputs.extend(default_info.other_outputs)

        # Collect test metadata, flattening nested wasi_suite targets.
        if WasiTestInfo in test:
            tests.append(test[WasiTestInfo])
        elif WasiTestSuiteInfo in test:
            tests.extend(test[WasiTestSuiteInfo].tests)
        else:
            fail("{} does not provide WasiTestInfo or WasiTestSuiteInfo".format(test.label))

    return [
        DefaultInfo(
            default_outputs = [ctx.actions.write("test_targets.txt", test_targets, has_content_based_path = False)],
            other_outputs = other_outputs,
        ),
        WasiTestSuiteInfo(tests = tests),
    ]

_wasi_test_suite_rule = rule(
    impl = _wasi_test_suite_impl,
    attrs = {
        "test_deps": attrs.list(attrs.dep(), default = []),
    },
)

def wasi_suite(name: str, tests: list[str], visibility = None):
    """Group WASI tests for `buck2 test` and aggregate metadata for `wasi_dist`."""
    kwargs = {}
    if visibility != None:
        kwargs["visibility"] = visibility

    _wasi_test_suite_rule(
        name = name,
        test_deps = tests,
        tests = tests,
        **kwargs
    )
