use test_wasm32_wasip3::http::wasi::http::types::{ErrorCode, Fields, Method, Request, Response};
use test_wasm32_wasip3::http::wit_future;
use test_wasm32_wasip3::http::{endpoint_request, endpoint_request_with_headers, request_line};
use test_wasm32_wasip3::http::{export, exports::wasi::http::handler::Guest};

const PLAIN: &str = "/plain";
const QUERY: &str = "/query?x=1";
const MULTI: &str = "/multi?a=1&b=2";
const ENCODED: &str = "/pct%2Fsegment?q=a%20b";
const ECHO: &str = "/echo?a=1&a=2&b=";

struct Component;
export!(Component);

impl Guest for Component {
    async fn handle(_request: Request) -> Result<Response, ErrorCode> {
        let (status, body) = endpoint_request(&Method::Get, PLAIN).await;
        assert_eq!(status, 200, "{PLAIN} did not reach its route");
        assert_eq!(body, b"plain");

        let (status, _) = endpoint_request(&Method::Get, "/plain?x=1").await;
        assert_eq!(status, 404, "the query should have reached the wire");

        let (status, body) = endpoint_request(&Method::Get, QUERY).await;
        assert_eq!(status, 200, "{QUERY} did not reach its route");
        assert_eq!(body, b"query");

        let (status, _) = endpoint_request(&Method::Get, "/query").await;
        assert_eq!(status, 404);

        let (status, body) = endpoint_request(&Method::Get, MULTI).await;
        assert_eq!(status, 200, "{MULTI} did not reach its route");
        assert_eq!(body, b"multi");
        let (status, _) = endpoint_request(&Method::Get, "/multi?b=2&a=1").await;
        assert_eq!(status, 404, "parameters should not be reordered");

        let (status, body) = endpoint_request(&Method::Get, ENCODED).await;
        assert_eq!(status, 200, "{ENCODED} did not reach its route");
        assert_eq!(body, b"encoded");

        // See: https://github.com/WebAssembly/WASI/issues/780.
        let (status, _, body) = endpoint_request_with_headers(&Method::Get, Some(""), &[]).await;
        assert_eq!(status, 200, "the empty path should be sent as /");
        assert_eq!(body, b"root");

        let (status, headers, _) =
            endpoint_request_with_headers(&Method::Get, Some(ECHO), &[]).await;
        assert_eq!(status, 200);
        assert_eq!(request_line(&headers, "x-request-path"), ECHO.as_bytes());

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
