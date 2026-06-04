load("@wasmono//:defs.bzl", "assemblyscript_binary")
load("//tools:conformance.bzl", "wasi_test")

def _config_for(name, conf):
    if conf != None:
        return conf

    path = "src/{}.json".format(name)
    return path if glob([path]) else None

def _asc_artifact(name):
    assemblyscript_binary(
        name = name,
        src = "src/{}.ts".format(name),
        visibility = ["//tests/..."],
    )

def _asc_test_for_runtime(test, name, runtime, manifest, target_compatible_with = None):
    test_target = "{}_{}".format(test.name, name)

    wasi_test(
        name = test_target,
        wasm = ":{}".format(test.name),
        runtime = runtime,
        manifest = manifest,
        config = test.config,
        target_compatible_with = target_compatible_with,
        visibility = ["//tests/..."],
    )

    return ":{}".format(test_target)

def asc_test(name, conf = None):
    config = _config_for(name, conf)

    _asc_artifact(name)

    return struct(
        config = config,
        name = name,
    )

def asc_tests_for_runtime(tests, name, runtime, manifest, target_compatible_with = None):
    return [
        _asc_test_for_runtime(
            test,
            name = name,
            runtime = runtime,
            manifest = manifest,
            target_compatible_with = target_compatible_with,
        )
        for test in tests
    ]
