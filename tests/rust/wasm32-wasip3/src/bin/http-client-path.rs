use test_wasm32_wasip3::http::wasi::http::types::{ErrorCode, Fields, Method, Request, Response};
use test_wasm32_wasip3::http::wit_future;
use test_wasm32_wasip3::http::{endpoint_request, request_line};
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
        let plain = endpoint_request(&Method::Get, Some(PLAIN), &[]).await;
        assert_eq!(plain.status, 200, "{PLAIN} did not reach its route");
        assert_eq!(plain.body, b"plain");
        assert!(plain.trailers.is_none(), "no trailer section was sent");

        let extra_query = endpoint_request(&Method::Get, Some("/plain?x=1"), &[]).await;
        assert_eq!(
            extra_query.status, 404,
            "the query should have reached the wire"
        );

        let query = endpoint_request(&Method::Get, Some(QUERY), &[]).await;
        assert_eq!(query.status, 200, "{QUERY} did not reach its route");
        assert_eq!(query.body, b"query");

        let no_query = endpoint_request(&Method::Get, Some("/query"), &[]).await;
        assert_eq!(no_query.status, 404);

        let multi = endpoint_request(&Method::Get, Some(MULTI), &[]).await;
        assert_eq!(multi.status, 200, "{MULTI} did not reach its route");
        assert_eq!(multi.body, b"multi");
        let reordered = endpoint_request(&Method::Get, Some("/multi?b=2&a=1"), &[]).await;
        assert_eq!(reordered.status, 404, "parameters should not be reordered");

        let encoded = endpoint_request(&Method::Get, Some(ENCODED), &[]).await;
        assert_eq!(encoded.status, 200, "{ENCODED} did not reach its route");
        assert_eq!(encoded.body, b"encoded");

        // See: https://github.com/WebAssembly/WASI/issues/780.
        let empty = endpoint_request(&Method::Get, Some(""), &[]).await;
        assert_eq!(empty.status, 200, "the empty path should be sent as /");
        assert_eq!(empty.body, b"root");

        let echo = endpoint_request(&Method::Get, Some(ECHO), &[]).await;
        assert_eq!(echo.status, 200);
        assert_eq!(
            request_line(&echo.headers, "x-request-path"),
            ECHO.as_bytes()
        );

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
