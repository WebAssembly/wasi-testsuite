use test_wasm32_wasip3::http::endpoint_request;
use test_wasm32_wasip3::http::wasi::http::types::{ErrorCode, Fields, Method, Request, Response};
use test_wasm32_wasip3::http::wit_future;
use test_wasm32_wasip3::http::{export, exports::wasi::http::handler::Guest};

struct Component;
export!(Component);

impl Guest for Component {
    async fn handle(_request: Request) -> Result<Response, ErrorCode> {
        // See https://github.com/WebAssembly/WASI/issues/949.
        let response = endpoint_request(&Method::Get, None, &[]).await;
        assert_eq!(
            response.status, 200,
            "an empty path and query should be sent as /"
        );
        assert_eq!(response.body, b"root");

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
