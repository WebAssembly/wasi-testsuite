"""Runtime descriptors used by generic WASI conformance tests.

A runtime target packages the parts that vary across the runtime matrix:
adapter plugin, executable, environment variable name, optional runner exclude
filter, and Buck labels. Language packages should depend on this provider
through `wasi_test`.
"""

WAMR_COMPATIBLE_WITH = [
    "config//os/constraints:linux",
    "config//cpu/constraints:x86_64",
]

WASMEDGE_COMPATIBLE_WITH = select({
    "config//os:linux": [],
    "config//os:macos": [],
    "config//os:windows": ["config//cpu/constraints:x86_64"],
    "DEFAULT": ["config//:none"],
})

WAZERO_COMPATIBLE_WITH = select({
    "config//os:linux": [],
    "config//os:macos": [],
    "config//os:windows": ["config//cpu/constraints:x86_64"],
    "DEFAULT": ["config//:none"],
})

WasiRuntimeInfo = provider(
    doc = "Provider describing one WASI runtime configuration.",
    fields = {
        # Python runtime adapter plugin loaded by the existing runner.
        "adapter": provider_field(Artifact),
        # Executable target providing RunInfo for the runtime binary.
        "runtime": provider_field(typing.Any),
        # Environment variable consumed by the adapter, e.g. WASMTIME.
        "runtime_env_var": provider_field(str),
        # Optional runner exclude filter for this runtime.
        "exclude_filter": provider_field(Artifact | None, default = None),
        # Buck test labels added to every test using this runtime.
        "labels": provider_field(list[str], default = []),
    },
)

def _wasi_runtime_impl(ctx: AnalysisContext) -> list[Provider]:
    return [
        DefaultInfo(),
        WasiRuntimeInfo(
            adapter = ctx.attrs.adapter,
            runtime = ctx.attrs.runtime,
            runtime_env_var = ctx.attrs.runtime_env_var,
            exclude_filter = ctx.attrs.exclude_filter,
            labels = ctx.attrs.labels,
        ),
    ]

wasi_runtime = rule(
    impl = _wasi_runtime_impl,
    attrs = {
        "adapter": attrs.source(doc = "Python adapter plugin file for wasi_test_runner."),
        "runtime": attrs.dep(providers = [RunInfo], doc = "Runtime executable target."),
        "runtime_env_var": attrs.string(doc = "Environment variable used to pass the runtime command to the adapter."),
        "exclude_filter": attrs.option(attrs.source(), default = None, doc = "Optional default exclude filter for this runtime."),
        "labels": attrs.list(attrs.string(), default = [], doc = "Labels propagated to tests that use this runtime."),
    },
    doc = "Create a WASI runtime descriptor consumed by `wasi_test`.",
)
