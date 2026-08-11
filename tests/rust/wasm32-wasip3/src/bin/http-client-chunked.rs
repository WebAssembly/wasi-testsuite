use test_wasm32_wasip3::http::endpoint_request;
use test_wasm32_wasip3::http::wasi::http::types::{ErrorCode, Fields, Method, Request, Response};
use test_wasm32_wasip3::http::wit_future;
use test_wasm32_wasip3::http::{export, exports::wasi::http::handler::Guest};

const CHUNKED: &str = "/chunked";
const TRAILERS: &str = "/trailers";

struct Component;
export!(Component);

fn value(trailers: &[(String, Vec<u8>)], name: &str) -> Vec<u8> {
    trailers
        .iter()
        .find(|(trailer, _)| trailer.eq_ignore_ascii_case(name))
        .unwrap_or_else(|| panic!("{name} should be present"))
        .1
        .clone()
}

impl Guest for Component {
    async fn handle(_request: Request) -> Result<Response, ErrorCode> {
        let chunked = endpoint_request(&Method::Get, Some(CHUNKED), &[]).await;
        assert_eq!(chunked.status, 200);
        assert_eq!(chunked.body, b"onetwothree");
        assert!(chunked.trailers.is_none(), "no trailer section was sent");

        let response = endpoint_request(&Method::Get, Some(TRAILERS), &[]).await;
        assert_eq!(response.status, 200);
        assert_eq!(response.body, b"payload");
        let trailers = response
            .trailers
            .expect("a trailer section should reach the guest");
        assert_eq!(value(&trailers, "x-checksum"), b"abc123");
        assert_eq!(value(&trailers, "x-parts"), b"1");

        let (trailers_tx, trailers_rx) = wit_future::new(|| Ok(None));
        drop(trailers_tx);
        let (response, _sent) = Response::new(Fields::new(), None, trailers_rx);
        response.set_status_code(200).unwrap();
        Ok(response)
    }
}

fn main() {
    unreachable!("main is a stub");
}
