"""Hermetic Rust toolchain.
Adapted from https://github.com/rue-language/rue/blob/trunk/toolchains/rust/defs.bzl
"""

load("@prelude//rust:rust_toolchain.bzl", "PanicRuntime", "RustToolchainInfo")
load("@wasmono//:defs.bzl", "host_arch", "host_os")
load(
    ":releases.bzl",
    "RUST_HOST_RELEASES",
    "RUST_STD_RELEASES",
    "RUST_VERSION",
    "rust_host_url",
    "rust_std_url",
)

# Map wasmono's canonical ``<arch>-<os>`` host key to the Rust host triple.
_HOST_TRIPLES = {
    "aarch64-linux": "aarch64-unknown-linux-gnu",
    "aarch64-macos": "aarch64-apple-darwin",
    "aarch64-windows": "aarch64-pc-windows-msvc",
    "x86_64-linux": "x86_64-unknown-linux-gnu",
    "x86_64-macos": "x86_64-apple-darwin",
    "x86_64-windows": "x86_64-pc-windows-msvc",
}

def host_rust_triple() -> str:
    """Return the Rust host triple for the machine running Buck."""
    key = "{}-{}".format(host_arch(), host_os())
    if key not in _HOST_TRIPLES:
        fail("Unsupported host platform for the hermetic Rust toolchain: '{}'".format(key))
    return _HOST_TRIPLES[key]

def download_rust_host(name: str, triple: str):
    """Download the combined ``rust`` package for ``triple``."""
    if triple not in RUST_HOST_RELEASES:
        fail("No pinned Rust host release for '{}'. Available: {}".format(
            triple,
            ", ".join(sorted(RUST_HOST_RELEASES.keys())),
        ))
    native.http_archive(
        name = name,
        urls = [rust_host_url(triple)],
        sha256 = RUST_HOST_RELEASES[triple],
        strip_prefix = "rust-{}-{}".format(RUST_VERSION, triple),
        type = "tar.xz",
    )

def download_rust_std(name: str, target: str):
    """Download the ``rust-std`` package for a wasm ``target``."""
    if target not in RUST_STD_RELEASES:
        fail("No pinned Rust std release for '{}'. Available: {}".format(
            target,
            ", ".join(sorted(RUST_STD_RELEASES.keys())),
        ))
    native.http_archive(
        name = name,
        urls = [rust_std_url(target)],
        sha256 = RUST_STD_RELEASES[target],
        strip_prefix = "rust-std-{}-{}".format(RUST_VERSION, target),
        type = "tar.xz",
    )

def _rust_tool_wrapper(ctx: AnalysisContext, name: str, host, host_inputs, component_bin: str, host_triple: str) -> RunInfo:
    if "windows" in host_triple:
        ext, script = ".bat", [
            "@echo off",
            cmd_args(host.project("rustc/bin"), format = "set PATH={};%PATH%"),
            cmd_args(host.project(component_bin + ".exe"), format = "{} %*"),
        ]
    else:
        ext, script = ".sh", [
            "#!/bin/sh",
            cmd_args(host.project("rustc/lib"), format = "export LD_LIBRARY_PATH=\"{}${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}\""),
            cmd_args(host.project("rustc/lib"), format = "export DYLD_LIBRARY_PATH=\"{}${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}\""),
            cmd_args(host.project(component_bin), format = "exec {} \"$@\""),
        ]
    wrapper, _ = ctx.actions.write(name + ext, script, is_executable = True, allow_args = True)
    return RunInfo(args = cmd_args(wrapper, hidden = host_inputs))

def _hermetic_rust_toolchain_impl(ctx: AnalysisContext) -> list[Provider]:
    host = ctx.attrs.host_distribution[DefaultInfo].default_outputs[0]
    host_triple = ctx.attrs.host_triple
    exe = ".exe" if "windows" in host_triple else ""

    rustc = host.project("rustc/bin/rustc" + exe)
    rustdoc = host.project("rustc/bin/rustdoc" + exe)

    host_inputs = (
        ctx.attrs.host_distribution[DefaultInfo].default_outputs +
        ctx.attrs.host_distribution[DefaultInfo].other_outputs
    )

    def tool(binary):
        return RunInfo(args = cmd_args(binary, hidden = host_inputs))

    clippy = _rust_tool_wrapper(ctx, "clippy_driver", host, host_inputs, "clippy-preview/bin/clippy-driver", host_triple)

    # Assemble a sysroot exposing only the lib/rustlib tree
    sysroot_entries = {
        "lib/rustlib/etc": host.project("rustc/lib/rustlib/etc"),
        "lib/rustlib/{}/bin".format(host_triple): host.project(
            "rustc/lib/rustlib/{}/bin".format(host_triple),
        ),
        "lib/rustlib/{}/lib".format(host_triple): host.project(
            "rust-std-{}/lib/rustlib/{}/lib".format(host_triple, host_triple),
        ),
    }

    for target, dist in ctx.attrs.std_distributions.items():
        std = dist[DefaultInfo].default_outputs[0]
        sysroot_entries["lib/rustlib/{}/lib".format(target)] = std.project(
            "rust-std-{}/lib/rustlib/{}/lib".format(target, target),
        )

    sysroot = ctx.actions.symlinked_dir("sysroot", sysroot_entries)

    return [
        DefaultInfo(),
        RustToolchainInfo(
            allow_lints = ctx.attrs.allow_lints,
            clippy_driver = clippy,
            clippy_toml = ctx.attrs.clippy_toml[DefaultInfo].default_outputs[0] if ctx.attrs.clippy_toml else None,
            compiler = tool(rustc),
            default_edition = ctx.attrs.default_edition,
            deny_lints = ctx.attrs.deny_lints,
            doctests = ctx.attrs.doctests,
            nightly_features = ctx.attrs.nightly_features,
            panic_runtime = PanicRuntime("unwind"),
            report_unused_deps = ctx.attrs.report_unused_deps,
            rustc_binary_flags = ctx.attrs.rustc_binary_flags,
            rustc_flags = ctx.attrs.rustc_flags,
            rustc_target_triple = ctx.attrs.rustc_target_triple,
            rustc_test_flags = ctx.attrs.rustc_test_flags,
            rustdoc = tool(rustdoc),
            rustdoc_flags = ctx.attrs.rustdoc_flags,
            sysroot_path = sysroot,
            warn_lints = ctx.attrs.warn_lints,
        ),
    ]

hermetic_rust_toolchain = rule(
    impl = _hermetic_rust_toolchain_impl,
    attrs = {
        "allow_lints": attrs.list(attrs.string(), default = []),
        "clippy_toml": attrs.option(attrs.dep(providers = [DefaultInfo]), default = None),
        "default_edition": attrs.option(attrs.string(), default = None),
        "deny_lints": attrs.list(attrs.string(), default = []),
        "doctests": attrs.bool(default = False),
        "host_distribution": attrs.exec_dep(
            providers = [DefaultInfo],
            doc = "Combined Rust distribution for the host (from download_rust_host).",
        ),
        "host_triple": attrs.string(doc = "Rust host triple of the build machine."),
        "nightly_features": attrs.bool(default = False),
        "report_unused_deps": attrs.bool(default = False),
        "rustc_binary_flags": attrs.list(attrs.arg(), default = []),
        "rustc_flags": attrs.list(attrs.arg(), default = []),
        "rustc_target_triple": attrs.string(),
        "rustc_test_flags": attrs.list(attrs.arg(), default = []),
        "rustdoc_flags": attrs.list(attrs.arg(), default = []),
        "std_distributions": attrs.dict(
            attrs.string(),
            attrs.exec_dep(providers = [DefaultInfo]),
            default = {},
            doc = "Map of wasm target triple to its rust-std distribution.",
        ),
        "warn_lints": attrs.list(attrs.string(), default = []),
    },
    is_toolchain_rule = True,
)

def _rustfmt_impl(ctx: AnalysisContext) -> list[Provider]:
    host = ctx.attrs.host_distribution[DefaultInfo].default_outputs[0]
    host_inputs = (
        ctx.attrs.host_distribution[DefaultInfo].default_outputs +
        ctx.attrs.host_distribution[DefaultInfo].other_outputs
    )
    rustfmt = _rust_tool_wrapper(ctx, "rustfmt", host, host_inputs, "rustfmt-preview/bin/rustfmt", ctx.attrs.host_triple)
    return [DefaultInfo(), rustfmt]

# Runnable rustfmt from the hermetic Rust distribution, e.g. `buck2 run toolchains//rust:rustfmt -- path/to/file.rs`. The edition is read from a discovered rustfmt.toml.
rustfmt = rule(
    impl = _rustfmt_impl,
    attrs = {
        "host_distribution": attrs.exec_dep(
            providers = [DefaultInfo],
            doc = "Combined Rust distribution for the host (from download_rust_host).",
        ),
        "host_triple": attrs.string(doc = "Rust host triple of the build machine."),
    },
)
