"""Rules for packaging WASI tests into a distribution archive."""

load("@prelude//utils:dicts.bzl", "update_x")
load("@prelude//utils:expect.bzl", "expect")
load("@prelude//utils:utils.bzl", "map_idx")
load("//tools:conformance.bzl", "WasiTestSuiteInfo")

def _single_output(dep, attr_name):
    outputs = dep[DefaultInfo].default_outputs
    expect(
        len(outputs) == 1,
        "{} must provide exactly one output, got {}",
        attr_name,
        len(outputs),
    )
    return outputs[0]

def _add_item(items, path, src):
    if src == None:
        return
    if path not in items:
        items[path] = src

def _wasi_dist_impl(ctx: AnalysisContext) -> list[Provider]:
    output = ctx.actions.declare_output("wasi-testsuite.tar.gz")
    spec = ctx.actions.declare_output("dist-spec.json")

    manifests = {}
    item_map = {}

    for suite in ctx.attrs.suites:
        for test in suite[WasiTestSuiteInfo].tests:
            expect(test.dist_dir != None, "{} does not set dist_dir in wasi_test", test.test_name)

            manifest_path = "{}/manifest.json".format(test.dist_dir)
            manifest = {
                "name": test.suite_name,
                "version": test.wasi_version,
            }

            update_x(
                manifests,
                manifest_path,
                manifest,
                fmt = "conflicting manifest metadata for {}: {} != {}",
            )

            _add_item(item_map, "{}/{}.wasm".format(test.dist_dir, test.test_name), test.wasm)
            _add_item(item_map, "{}/{}.json".format(test.dist_dir, test.test_name), test.config)

            for guest_name, fixture_dir in test.fixture_dirs.items():
                _add_item(item_map, "{}/{}".format(test.dist_dir, guest_name), fixture_dir)

    for dst, src in ctx.attrs.extra_files.items():
        _add_item(item_map, dst, _single_output(src, "extra_files[{}]".format(dst)))

    items = [
        {
            "dst": path,
            "src": src,
        }
        for path, src in item_map.items()
    ]

    ctx.actions.write_json(spec, {
        "root": ctx.attrs.root,
        "manifests": [
            {
                "dst": path,
                "content": content,
            }
            for path, content in manifests.items()
        ],
        "items": items,
    }, with_inputs = True)

    ctx.actions.run(
        cmd_args(
            ctx.attrs._package_script[RunInfo],
            "--spec",
            spec,
            "--output",
            output.as_output(),
            hidden = map_idx("src", items),
        ),
        category = "wasi_dist",
    )

    return [DefaultInfo(default_output = output)]

wasi_dist = rule(
    impl = _wasi_dist_impl,
    attrs = {
        "root": attrs.string(default = "wasi-testsuite"),
        "suites": attrs.list(
            attrs.dep(providers = [WasiTestSuiteInfo]),
            default = [],
            doc = "WASI test suite targets to include in the archive.",
        ),
        "extra_files": attrs.dict(
            key = attrs.string(),
            value = attrs.dep(providers = [DefaultInfo]),
            default = {},
            doc = "Additional files or directories to include at archive-relative paths.",
        ),
        "_package_script": attrs.exec_dep(
            default = "//tools:package_dist",
            providers = [RunInfo],
        ),
    },
    doc = "Create a deterministic wasi-testsuite tarball from declared inputs.",
)
