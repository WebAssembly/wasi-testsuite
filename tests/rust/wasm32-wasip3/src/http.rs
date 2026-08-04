wit_bindgen::generate!({
    inline: r"
	package wasi-testsuite:test;

	world http-test {
	    include wasi:http/service@0.3.0;
	    import wasi:cli/environment@0.3.0;
	}
    ",
    additional_derives: [PartialEq, Eq, Hash, Clone],
    pub_export_macro: true,
    default_bindings_module: "test_wasm32_wasip3::http",
    features:["clocks-timezone"],
    generate_all
});

use wasi::cli::environment;
use wasi::http::client;
use wasi::http::types::{Fields, Method, Request, Response, Scheme, StatusCode};

pub fn endpoint_authority() -> String {
    environment::get_environment()
        .into_iter()
        .find(|(name, _)| name == "HTTP_ENDPOINT")
        .map(|(_, value)| value)
        .expect("HTTP_ENDPOINT must be set by the test runner")
}

pub async fn endpoint_request(method: &Method, path: &str) -> (StatusCode, Vec<u8>) {
    let (trailers_tx, trailers_rx) = wit_future::new(|| Ok(None));
    drop(trailers_tx);

    let (request, _sent) = Request::new(Fields::new(), None, trailers_rx, None);
    request.set_method(method).unwrap();
    request.set_scheme(Some(&Scheme::Http)).unwrap();
    request.set_authority(Some(&endpoint_authority())).unwrap();
    request.set_path_with_query(Some(path)).unwrap();

    let response = client::send(request).await.expect("send should succeed");
    let status = response.get_status_code();

    let (_, result_rx) = wit_future::new(|| Ok(()));
    let (body_rx, trailers) = Response::consume_body(response, result_rx);
    let body = body_rx.collect().await;
    assert!(trailers.await.unwrap().is_none());

    (status, body)
}
