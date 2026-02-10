wit_bindgen::generate!({
    inline: r"
	package wasi-testsuite:test;

	world test {
	    include wasi:random/imports@0.3.0-rc-2026-01-06;
	}
    ",
    features:["clocks-timezone"],
    pub_export_macro: true,
    default_bindings_module: "test_wasm32_wasip3::random",
    additional_derives: [PartialEq, Eq],
    generate_all
});
