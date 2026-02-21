wit_bindgen::generate!({
    inline: r"
	package wasi-testsuite:test;

	world clocks-test {
		include wasi:clocks/imports@0.3.0-rc-2026-02-09;
	}
    ",
    features:["clocks-timezone"],
    pub_export_macro: true,
    default_bindings_module: "test_wasm32_wasip3::clocks",
    generate_all
});

use self::wasi::clocks::monotonic_clock::Duration;

pub const NANOSECOND: Duration = 1;
pub const MICROSECOND: Duration = NANOSECOND * 1_000;
pub const MILLISECOND: Duration = MICROSECOND * 1_000;
pub const SECOND: Duration = MILLISECOND * 1_000;
pub const MINUTE: Duration = SECOND * 60;
pub const HOUR: Duration = MINUTE * 60;
pub const DAY: Duration = HOUR * 24;
