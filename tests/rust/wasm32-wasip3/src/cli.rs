wit_bindgen::generate!({
    inline: r"
	package wasi-testsuite:test;

	world cli-test {
		include wasi:cli/command@0.3.0-rc-2026-02-09;
	}
    ",
    features:["clocks-timezone"],
    pub_export_macro: true,
    default_bindings_module: "test_wasm32_wasip3::cli",
    additional_derives: [PartialEq, Eq],
    generate_all
});
