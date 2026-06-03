load("//tools:conformance.bzl", "wasi_test")

_DEFAULT_FIXTURE_DIRS = {
    "fs-tests.dir": "src/fs-tests.dir",
}

def _config_for(name, conf):
    if conf != None:
        return conf

    path = "src/{}.json".format(name)
    return path if glob([path]) else None

def _fixture_dirs_for(config, dirs):
    if dirs != None:
        return dirs
    return _DEFAULT_FIXTURE_DIRS if config else {}

def _c_artifact(name):
    native.cxx_binary(
        name = name,
        srcs = ["src/{}.c".format(name)],
        _cxx_toolchain = "toolchains//:cxx_wasi_p1",
        visibility = ["//tests/..."],
    )

def _c_test_for_runtime(test, name, runtime, manifest):
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

def c_test(name, conf = None, dirs = None):
    config = _config_for(name, conf)
    fixture_dirs = _fixture_dirs_for(config, dirs)

    _c_artifact(name)

    return struct(
        name = name,
        config = config,
        fixture_dirs = fixture_dirs,
    )

def c_tests_for_runtime(tests, name, runtime, manifest):
    return [
        _c_test_for_runtime(
            test,
            name = name,
            runtime = runtime,
            manifest = manifest,
        )
        for test in tests
    ]
