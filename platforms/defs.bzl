"""Platform helpers.

The incoming-transition alias pattern is adapted from buck2-rustc-bootstrap.
"""

def _transition_alias_impl(ctx):
    return ctx.attrs.actual.providers

transition_alias = rule(
    impl = _transition_alias_impl,
    attrs = {
        "actual": attrs.dep(providers = [DefaultInfo]),
    },
    supports_incoming_transition = True,
)

def _transition_to_platform_impl(ctx):
    configuration = ctx.attrs.platform[PlatformInfo].configuration
    transition = set(configuration.constraints)
    transition_label = "{}-transitioned".format(ctx.label.raw_target())

    def transition_impl(platform):
        constraints = dict(configuration.constraints)
        for setting, value in platform.configuration.constraints.items():
            if setting not in transition:
                constraints[setting] = value

        return PlatformInfo(
            label = transition_label,
            configuration = ConfigurationInfo(
                constraints = constraints,
                values = platform.configuration.values,
            ),
        )

    return [
        DefaultInfo(),
        TransitionInfo(impl = transition_impl),
    ]

transition_to_platform = rule(
    impl = _transition_to_platform_impl,
    attrs = {
        "platform": attrs.dep(providers = [PlatformInfo]),
    },
    is_configuration_rule = True,
)
