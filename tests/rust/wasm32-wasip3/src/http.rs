wit_bindgen::generate!({
    inline: r"
	package wasi-testsuite:test;

	world http-test {
	    include wasi:http/service@0.3.0-rc-2026-02-09;
	}
    ",
    additional_derives: [PartialEq, Eq, Hash, Clone],
    pub_export_macro: true,
    default_bindings_module: "test_wasm32_wasip3::http",
    features:["clocks-timezone"],
    generate_all
});
