use test_wasm32_wasip3::http::endpoint_request;
use test_wasm32_wasip3::http::wasi::http::types::{ErrorCode, Fields, Method, Request, Response};
use test_wasm32_wasip3::http::wit_future;
use test_wasm32_wasip3::http::{export, exports::wasi::http::handler::Guest};

struct Component;
export!(Component);

impl Guest for Component {
    async fn handle(_request: Request) -> Result<Response, ErrorCode> {
        let (status, body) = endpoint_request(&Method::Get, "/ok").await;
        assert_eq!(status, 200);
        assert!(body.is_empty());

        let (status, body) = endpoint_request(&Method::Get, "/created").await;
        assert_eq!(status, 201);
        assert_eq!(body, b"made".to_vec());

        let (status, _) = endpoint_request(&Method::Get, "/teapot").await;
        assert_eq!(status, 418);

        let (status, body) = endpoint_request(&Method::Get, "/boom").await;
        assert_eq!(status, 500);
        assert_eq!(body, b"nope".to_vec());

        let (status, _) = endpoint_request(&Method::Get, "/unrouted").await;
        assert_eq!(status, 404);

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
