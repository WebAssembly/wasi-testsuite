use test_wasm32_wasip3::http::endpoint_request;
use test_wasm32_wasip3::http::wasi::http::types::{ErrorCode, Fields, Method, Request, Response};
use test_wasm32_wasip3::http::wit_future;
use test_wasm32_wasip3::http::{export, exports::wasi::http::handler::Guest};

struct Component;
export!(Component);

impl Guest for Component {
    async fn handle(_request: Request) -> Result<Response, ErrorCode> {
        let ok = endpoint_request(&Method::Get, Some("/ok"), &[]).await;
        assert_eq!(ok.status, 200);
        assert!(ok.body.is_empty());
        assert!(ok.trailers.is_none(), "no trailer section was sent");

        let created = endpoint_request(&Method::Get, Some("/created"), &[]).await;
        assert_eq!(created.status, 201);
        assert_eq!(created.body, b"made".to_vec());

        let teapot = endpoint_request(&Method::Get, Some("/teapot"), &[]).await;
        assert_eq!(teapot.status, 418);

        let boom = endpoint_request(&Method::Get, Some("/boom"), &[]).await;
        assert_eq!(boom.status, 500);
        assert_eq!(boom.body, b"nope".to_vec());

        let missing = endpoint_request(&Method::Get, Some("/unrouted"), &[]).await;
        assert_eq!(missing.status, 404);

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
