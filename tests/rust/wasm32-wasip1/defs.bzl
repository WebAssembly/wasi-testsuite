load("//platforms:defs.bzl", "transition_alias")
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
    return _DEFAULT_FIXTURE_DIRS if config else {}

def _rust_artifact(name, deps):
    native.rust_binary(
        name = name,
        crate = name.replace("-", "_"),
        crate_root = "src/bin/{}.rs".format(name),
        srcs = ["src/bin/{}.rs".format(name)],
        edition = "2024",
        deps = deps,
        default_target_platform = "//platforms:wasm32_wasip1",
        _cxx_toolchain = "toolchains//:rust_linker",
        _rust_toolchain = "toolchains//:rust_wasi_p1",
        visibility = ["//tests/..."],
    )

    transition_alias(
        name = "{}_wasip1".format(name),
        actual = ":{}".format(name),
        incoming_transition = "//platforms:wasm32_wasip1_transition",
        visibility = ["//tests/..."],
    )

def _rust_test_for_runtime(test, name, runtime, manifest, target_compatible_with = None):
    test_target = "{}_{}".format(test.name, name)

    wasi_test(
        name = test_target,
        wasm = ":{}_wasip1".format(test.name),
        runtime = runtime,
        manifest = manifest,
        config = test.config,
        fixture_dirs = test.fixture_dirs,
        test_name = test.name,
        target_compatible_with = target_compatible_with,
        visibility = ["//tests/..."],
    )

    return ":{}".format(test_target)

def rust_test(name, conf = None, dirs = None, deps = []):
    config = _config_for(name, conf)
    fixture_dirs = _fixture_dirs_for(config, dirs)

    _rust_artifact(name, deps = deps)

    return struct(
        config = config,
        fixture_dirs = fixture_dirs,
        name = name,
    )

def rust_tests_for_runtime(tests, name, runtime, manifest, target_compatible_with = None):
    return [
        _rust_test_for_runtime(
            test,
            name = name,
            runtime = runtime,
            manifest = manifest,
            target_compatible_with = target_compatible_with,
        )
        for test in tests
    ]
