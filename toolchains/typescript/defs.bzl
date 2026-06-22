"""Hermetic TypeScript/JS tooling.

Installs oxc's linter (oxlint) and formatter (oxfmt) via npm using the shared
Node distribution, and exposes them as runnable targets, e.g.
``buck2 run toolchains//typescript:oxlint -- path/to/file.ts``.
"""

load("@wasmono//toolchains/wasm:node.bzl", "NodeInfo")

OXLINT_VERSION = "1.69.0"
OXFMT_VERSION = "0.54.0"

def _install_oxc_impl(ctx: AnalysisContext) -> list[Provider]:
    node_info = ctx.attrs.node[NodeInfo]
    out_dir = ctx.actions.declare_output("oxc_workspace", dir = True)

    cmd = cmd_args(
        node_info.npm,
        "install",
        "--prefix",
        out_dir.as_output(),
        "--no-package-lock",
        "oxlint@{}".format(ctx.attrs.oxlint_version),
        "oxfmt@{}".format(ctx.attrs.oxfmt_version),
    )

    ctx.actions.run(
        cmd,
        category = "npm_install_oxc",
        local_only = True,  # needs network access
    )

    return [DefaultInfo(default_output = out_dir)]

install_oxc = rule(
    impl = _install_oxc_impl,
    attrs = {
        "node": attrs.exec_dep(providers = [NodeInfo]),
        "oxfmt_version": attrs.string(default = OXFMT_VERSION),
        "oxlint_version": attrs.string(default = OXLINT_VERSION),
    },
)

def _oxc_tool_impl(ctx: AnalysisContext) -> list[Provider]:
    node_info = ctx.attrs.node[NodeInfo]
    workspace = ctx.attrs.workspace[DefaultInfo].default_outputs[0]
    binary = workspace.project("node_modules/.bin/{}".format(ctx.attrs.tool))

    # The npm bin entries are Node.js launchers (#!/usr/bin/env node), so run
    # them through the hermetic node rather than relying on a system node/PATH.
    return [
        DefaultInfo(default_output = binary),
        RunInfo(args = cmd_args(
            node_info.node,
            binary,
            hidden = ctx.attrs.workspace[DefaultInfo].default_outputs,
        )),
    ]

oxc_tool = rule(
    impl = _oxc_tool_impl,
    attrs = {
        "node": attrs.exec_dep(providers = [NodeInfo]),
        "tool": attrs.string(doc = "Binary name in node_modules/.bin (oxlint or oxfmt)."),
        "workspace": attrs.dep(providers = [DefaultInfo], doc = "install_oxc output."),
    },
)
