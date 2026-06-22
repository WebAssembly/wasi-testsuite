"""Download rules for WASI runtime binaries used by the test suite."""

load("@wasmono//toolchains/wasm:node.bzl", "NodeInfo")
load("@wasmono//:defs.bzl", "host_arch", "host_os")
load(":releases.bzl", "WAMR_RELEASES", "WASMEDGE_RELEASES", "WASMTIME_RELEASES", "WAZERO_RELEASES")

DEFAULT_JCO_VERSION = "1.24.1"
DEFAULT_NODE_VERSION = "24.16.0"
DEFAULT_WAMR_VERSION = "2.4.4"
DEFAULT_WASMEDGE_VERSION = "0.17.0"
DEFAULT_WASMTIME_VERSION = "45.0.0"
DEFAULT_WAZERO_VERSION = "1.12.0"

def _runtime_platform() -> str:
    return "{}-{}".format(host_arch(), host_os())

def _runtime_release(releases, runtime_name: str, version: str, target_compatible_with = []):
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

def _jco_runtime_command_impl(ctx: AnalysisContext) -> list[Provider]:
    node_info = ctx.attrs.node[NodeInfo]
    jco_workspace = ctx.attrs.jco[DefaultInfo].default_outputs[0]
    jco_js = cmd_args(
        jco_workspace,
        format = "{}/node_modules/@bytecodealliance/jco/src/jco.js",
    )

    run = cmd_args(
        node_info.node,
        "--experimental-wasm-jspi",
        ctx.attrs.runner,
        "--jco",
        jco_js,
        "--jco-workspace",
        jco_workspace,
    )

    return [
        DefaultInfo(default_output = ctx.attrs.runner),
        RunInfo(args = run),
    ]

_jco_runtime_command = rule(
    impl = _jco_runtime_command_impl,
    attrs = {
        "jco": attrs.dep(providers = [DefaultInfo]),
        "node": attrs.dep(providers = [NodeInfo]),
        "runner": attrs.source(),
    },
)

def jco_runtime_command(
        name: str,
        jco: str,
        node: str,
        runner: str,
        visibility = None):
    """Create a command for running WASI P3 command components through jco."""
    kwargs = {}
    if visibility != None:
        kwargs["visibility"] = visibility

    _jco_runtime_command(
        name = name,
        jco = jco,
        node = node,
        runner = runner,
        **kwargs
    )

def _download_runtime(
        name: str,
        releases,
        runtime_name: str,
        version: str,
        target_compatible_with = []):
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
        target_compatible_with = []):
    """Download a prebuilt WAMR (iwasm) runtime."""
    _download_runtime(name, WAMR_RELEASES, "wamr", version, target_compatible_with)

def download_wazero_runtime(
        name: str,
        version: str = DEFAULT_WAZERO_VERSION,
        target_compatible_with = []):
    """Download a prebuilt Wazero runtime."""
    _download_runtime(name, WAZERO_RELEASES, "wazero", version, target_compatible_with)

def download_wasmedge_runtime(
        name: str,
        version: str = DEFAULT_WASMEDGE_VERSION,
        target_compatible_with = []):
    """Download a prebuilt WasmEdge runtime."""
    _download_runtime(name, WASMEDGE_RELEASES, "wasmedge", version, target_compatible_with)
