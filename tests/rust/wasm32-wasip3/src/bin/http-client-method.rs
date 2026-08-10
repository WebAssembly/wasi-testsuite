use test_wasm32_wasip3::http::endpoint_request;
use test_wasm32_wasip3::http::wasi::http::types::{ErrorCode, Fields, Method, Request, Response};
use test_wasm32_wasip3::http::wit_future;
use test_wasm32_wasip3::http::{export, exports::wasi::http::handler::Guest};

const PATH: &str = "/method";

struct Component;
export!(Component);

impl Guest for Component {
    async fn handle(_request: Request) -> Result<Response, ErrorCode> {
        for method in [
            Method::Get,
            Method::Post,
            Method::Put,
            Method::Delete,
            Method::Patch,
            Method::Options,
        ] {
            let expected = match &method {
                Method::Get => "GET",
                Method::Post => "POST",
                Method::Put => "PUT",
                Method::Delete => "DELETE",
                Method::Patch => "PATCH",
                Method::Options => "OPTIONS",
                other => panic!("unexpected method {other:?}"),
            };
            let (status, body) = endpoint_request(&method, PATH).await;
            assert_eq!(status, 200, "{expected} did not reach its route");
            assert_eq!(body, expected.as_bytes().to_vec());
        }

        let (status, _) = endpoint_request(&Method::Head, PATH).await;
        assert_eq!(status, 200, "HEAD did not reach its route");

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
