"""Local C/C++ toolchain helpers.

Exposes a runnable ``clang-format`` taken from the same hermetic wasi-sdk
distribution used by the C/C++ toolchains, e.g.
``buck2 run toolchains//cxx:clang-format -- -i path/to/file.c``.
"""

load("@wasmono//toolchains/cxx/wasi:defs.bzl", "WasiSdkDistributionInfo")

def _clang_format_impl(ctx: AnalysisContext) -> list[Provider]:
    dist_info = ctx.attrs.distribution[WasiSdkDistributionInfo]
    dist = ctx.attrs.distribution[DefaultInfo].default_outputs[0]
    exe = ".exe" if dist_info.os == "windows" else ""
    clang_format = dist.project("{}/clang-format{}".format(dist_info.bin_path, exe))

    dist_outputs = (
        ctx.attrs.distribution[DefaultInfo].default_outputs +
        ctx.attrs.distribution[DefaultInfo].other_outputs
    )

    return [
        DefaultInfo(default_output = clang_format),
        RunInfo(args = cmd_args(clang_format, hidden = dist_outputs)),
    ]

clang_format = rule(
    impl = _clang_format_impl,
    attrs = {
        "distribution": attrs.exec_dep(
            providers = [WasiSdkDistributionInfo],
            doc = "wasi-sdk distribution (from download_wasi_sdk) providing clang-format.",
        ),
    },
)
