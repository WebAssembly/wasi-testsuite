"""Download rules for WASI runtime binaries used by the test suite."""

load("@prelude//utils:expect.bzl", "expect")
load("@wasmono//toolchains/wasm:node.bzl", "NodeInfo")
load("@wasmono//:defs.bzl", "host_arch", "host_os")
load(
    ":releases.bzl",
    "JBANG_RELEASES",
    "JDK_RELEASES",
    "WAMR_RELEASES",
    "WASMEDGE_RELEASES",
    "WASMTIME_RELEASES",
    "WAZERO_RELEASES",
)

DEFAULT_JBANG_VERSION = "0.142.0"
DEFAULT_JCO_VERSION = "1.35.0"
DEFAULT_JDK_VERSION = "21.0.13+9"
DEFAULT_NODE_VERSION = "26.8.2"
DEFAULT_WAMR_VERSION = "2.4.5"
DEFAULT_WASMEDGE_VERSION = "0.17.1"
DEFAULT_WASMTIME_VERSION = "49.0.3"
DEFAULT_WAZERO_VERSION = "1.12.0"

def _runtime_platform() -> str:
    return "{}-{}".format(host_arch(), host_os())

def _runtime_release(releases, runtime_name: str, version: str, target_compatible_with = []):
    platform = _runtime_platform()
    expect(
        version in releases,
        "Unknown {} version '{}'. Available: {}",
        runtime_name,
        version,
        ", ".join(releases.keys()),
    )

    release = releases[version]
    if platform not in release and "default" in release:
        return release["default"]
    if platform not in release and target_compatible_with:
        for fallback in release.values():
            return fallback

    expect(
        platform in release,
        "No {} release for platform '{}'. Available: {}",
        runtime_name,
        platform,
        ", ".join(release.keys()),
    )
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
        format = "{}/node_modules/@bytecodealliance/jco/dist/jco.js",
    )

    run = cmd_args(
        node_info.node,
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

def _endive_runtime_command_impl(ctx: AnalysisContext) -> list[Provider]:
    java = ctx.attrs.jdk[RunInfo]
    jar = ctx.actions.declare_output("endive-runner.jar")
    ctx.actions.run(
        cmd_args(
            ctx.attrs.jbang[RunInfo],
            "--quiet",
            "export",
            "fatjar",
            "--jdk-providers=javahome",
            "--force",
            "--output",
            jar.as_output(),
            ctx.attrs.runner,
            hidden = java,
        ),
        # JAVA_HOME is the pinned JDK root, two levels above `bin/java`.
        env = {"JAVA_HOME": cmd_args(ctx.attrs.jdk[DefaultInfo].default_outputs[0], parent = 2)},
        category = "jbang_export",
        # jbang resolves the endive jars from Maven Central.
        local_only = True,
    )

    return [
        DefaultInfo(default_output = jar),
        RunInfo(args = cmd_args(java, "-jar", jar)),
    ]

_endive_runtime_command = rule(
    impl = _endive_runtime_command_impl,
    attrs = {
        "jbang": attrs.exec_dep(providers = [RunInfo]),
        "jdk": attrs.dep(providers = [RunInfo]),
        "runner": attrs.source(),
    },
)

def endive_runtime_command(
        name: str,
        jbang: str,
        jdk: str,
        runner: str,
        target_compatible_with = [],
        visibility = None):
    """Build the endive jbang runner into a fat jar and run it on the pinned JDK."""
    kwargs = {}
    if target_compatible_with:
        kwargs["target_compatible_with"] = target_compatible_with
    if visibility != None:
        kwargs["visibility"] = visibility

    _endive_runtime_command(
        name = name,
        jbang = jbang,
        jdk = jdk,
        runner = runner,
        **kwargs
    )

def _download_runtime(
        name: str,
        releases,
        runtime_name: str,
        version: str,
        target_compatible_with = [],
        append_exe: bool = True):
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
        binary = release["binary"] + (".exe" if append_exe and host_os() == "windows" else ""),
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

def download_jbang(
        name: str,
        version: str = DEFAULT_JBANG_VERSION,
        target_compatible_with = []):
    """Download jbang, used to build the endive runner."""
    _download_runtime(name, JBANG_RELEASES, "jbang", version, target_compatible_with, append_exe = False)

def download_jdk(
        name: str,
        version: str = DEFAULT_JDK_VERSION,
        target_compatible_with = []):
    """Download a prebuilt JDK, used to build and run the endive runner."""
    _download_runtime(name, JDK_RELEASES, "jdk", version, target_compatible_with)
