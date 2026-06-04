"""Download rules for WASI runtime binaries used by the test suite."""

load("@wasmono//:defs.bzl", "host_arch", "host_os")
load(":releases.bzl", "WAMR_RELEASES", "WASMEDGE_RELEASES", "WASMTIME_RELEASES", "WAZERO_RELEASES")

DEFAULT_WAMR_VERSION = "2.4.4"
DEFAULT_WASMEDGE_VERSION = "0.17.0"
DEFAULT_WASMTIME_VERSION = "45.0.0"
DEFAULT_WAZERO_VERSION = "1.12.0"

def _runtime_platform() -> str:
    return "{}-{}".format(host_arch(), host_os())

def _runtime_release(releases, runtime_name: str, version: str, target_compatible_with: list[str] = []):
    platform = _runtime_platform()
    if version not in releases:
        fail("Unknown {} version '{}'. Available: {}".format(
            runtime_name,
            version,
            ", ".join(releases.keys()),
        ))

    release = releases[version]
    if platform not in release and target_compatible_with:
        for fallback in release.values():
            return fallback

    if platform not in release:
        fail("No {} release for platform '{}'. Available: {}".format(
            runtime_name,
            platform,
            ", ".join(release.keys()),
        ))
    return release[platform]

def _runtime_distribution_impl(ctx: AnalysisContext) -> list[Provider]:
    dist = ctx.attrs.dist[DefaultInfo].default_outputs[0]
    binary_path = ctx.attrs.binary

    if ctx.attrs.prefix:
        binary_path = "{}/{}".format(ctx.attrs.prefix, ctx.attrs.binary)

    binary = dist.project(binary_path)

    run = cmd_args(
        [binary],
        hidden = [
            ctx.attrs.dist[DefaultInfo].default_outputs,
            ctx.attrs.dist[DefaultInfo].other_outputs,
        ],
    )

    return [
        DefaultInfo(default_output = binary),
        RunInfo(args = run),
    ]

_runtime_distribution = rule(
    impl = _runtime_distribution_impl,
    attrs = {
        "dist": attrs.dep(providers = [DefaultInfo]),
        "binary": attrs.string(),
        "prefix": attrs.string(default = ""),
    },
)

def _download_runtime(
        name: str,
        releases,
        runtime_name: str,
        version: str,
        target_compatible_with: list[str] = []):
    release = _runtime_release(releases, runtime_name, version, target_compatible_with)
    kwargs = {}
    if target_compatible_with:
        kwargs["target_compatible_with"] = target_compatible_with

    native.http_archive(
        name = name + "-archive",
        urls = [release["url"]],
        sha256 = release["shasum"],
        **kwargs
    )

    _runtime_distribution(
        name = name,
        dist = ":" + name + "-archive",
        binary = release["binary"] + (".exe" if host_os() == "windows" else ""),
        prefix = release.get("prefix", ""),
        visibility = ["PUBLIC"],
        **kwargs
    )

def download_wasmtime_runtime(name: str, version: str = DEFAULT_WASMTIME_VERSION):
    """Download a prebuilt Wasmtime runtime."""
    _download_runtime(name, WASMTIME_RELEASES, "wasmtime", version)

def download_wamr_runtime(
        name: str,
        version: str = DEFAULT_WAMR_VERSION,
        target_compatible_with: list[str] = []):
    """Download a prebuilt WAMR (iwasm) runtime."""
    _download_runtime(name, WAMR_RELEASES, "wamr", version, target_compatible_with)

def download_wazero_runtime(name: str, version: str = DEFAULT_WAZERO_VERSION):
    """Download a prebuilt Wazero runtime."""
    _download_runtime(name, WAZERO_RELEASES, "wazero", version)

def download_wasmedge_runtime(name: str, version: str = DEFAULT_WASMEDGE_VERSION):
    """Download a prebuilt WasmEdge runtime."""
    _download_runtime(name, WASMEDGE_RELEASES, "wasmedge", version)
