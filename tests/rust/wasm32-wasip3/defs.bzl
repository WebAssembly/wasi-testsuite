load("@wasmono//:defs.bzl", "wasm_component")
load("//tools:conformance.bzl", "wasi_test")

_DEFAULT_FIXTURE_DIRS = {
    "fs-tests.dir": "src/bin/fs-tests.dir",
}

def _config_for(name, conf):
    if conf != None:
        return conf

    path = "src/bin/{}.json".format(name)
    return path if glob([path]) else None

def _fixture_dirs_for(config, dirs):
    if dirs != None:
        return dirs
    return _DEFAULT_FIXTURE_DIRS if config and config.startswith("src/bin/filesystem-") else {}

def _rust_p3_artifact(name, deps, wit_srcs):
    module_name = "{}_module".format(name)

    native.rust_binary(
        name = module_name,
        crate = name.replace("-", "_"),
        crate_root = "src/bin/{}.rs".format(name),
        srcs = ["src/bin/{}.rs".format(name)] + wit_srcs,
        edition = "2024",
        env = {"CARGO_MANIFEST_DIR": "."},
        deps = deps,
        default_target_platform = "//platforms:wasm32_wasip2",
        _cxx_toolchain = "toolchains//:rust_linker",
        _rust_toolchain = "toolchains//:rust",
        visibility = ["//tests/..."],
    )

    wasm_component(
        name = name,
        module = ":{}".format(module_name),
        skip_validation = True,
        visibility = ["//tests/..."],
    )

def _rust_p3_test_for_runtime(test, name, runtime, manifest):
    test_target = "{}_{}".format(test.name, name)

    wasi_test(
        name = test_target,
        wasm = ":{}".format(test.name),
        runtime = runtime,
        manifest = manifest,
        config = test.config,
        fixture_dirs = test.fixture_dirs,
        visibility = ["//tests/..."],
    )

    return ":{}".format(test_target)

def rust_p3_test(name, deps, wit_srcs, conf = None, dirs = None):
    config = _config_for(name, conf)
    fixture_dirs = _fixture_dirs_for(config, dirs)

    _rust_p3_artifact(name, deps = deps, wit_srcs = wit_srcs)

    return struct(
        config = config,
        fixture_dirs = fixture_dirs,
        name = name,
    )

def rust_p3_tests_for_runtime(tests, name, runtime, manifest):
    return [
        _rust_p3_test_for_runtime(
            test,
            name = name,
            runtime = runtime,
            manifest = manifest,
        )
        for test in tests
    ]
