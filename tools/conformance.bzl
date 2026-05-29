"""Rules for turning Buck-built wasm artifacts into WASI conformance tests.

The build target that produces a `.wasm` file should stay language-specific
(`cxx_binary`, `rust_binary`, `assemblyscript_binary`, ...). The generic
`wasi_test` rule adds the runtime dimension by pairing that artifact with a
`WasiRuntimeInfo` provider and delegating execution to the existing
`wasi_test_runner`.

`wasi_suite` is reporting metadata consumed by the Python runner. Runtime
grouping should be represented with Buck `test_suite` targets, for example a
package-level `test_suite(name = "wasmtime", tests = [":lseek_wasmtime"])`.
"""

load("@prelude//decls:common.bzl", "buck")
load("@prelude//test:inject_test_run_info.bzl", "inject_test_run_info")
load(":runtime.bzl", "WasiRuntimeInfo")

def wasi_suite(name: str, version: str):
    """Create suite metadata written into the staged runner manifest."""
    return struct(
        name = name,
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
        suite,
        config = None,
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
        suite: Metadata from `wasi_suite`.
        config: Optional runner JSON config for this test.
        fixture_dirs: Mutable preopened directories staged for the runner.
        exclude_filter: Optional runner exclude filter overriding the runtime default.
        test_name: Optional runner test name; inferred from `wasm` labels.
        labels: Extra Buck test labels.
        visibility: Optional Buck visibility.
    """
    kwargs = {}
    if visibility != None:
        kwargs["visibility"] = visibility

    _wasi_test_rule(
        name = name,
        wasm = wasm,
        runtime = runtime,
        suite_name = suite.name,
        wasi_version = suite.version,
        test_name = test_name or _infer_test_name(wasm),
        config = config,
        fixture_dirs = fixture_dirs,
        exclude_filter = exclude_filter,
        labels = labels,
        **kwargs
    )
