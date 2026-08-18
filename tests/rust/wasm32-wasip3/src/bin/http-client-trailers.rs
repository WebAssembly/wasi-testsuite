use test_wasm32_wasip3::http::wasi::http::types::{ErrorCode, Fields, Request, Response};
use test_wasm32_wasip3::http::wit_future;
use test_wasm32_wasip3::http::{EndpointResponse, echoed, echoed_trailer, request_line};
use test_wasm32_wasip3::http::{consume_response, send_with_trailers};
use test_wasm32_wasip3::http::{export, exports::wasi::http::handler::Guest};

const ECHO_HEADERS: &str = "/echo-headers";
const ECHO_BODY: &str = "/echo-body";

struct Component;
export!(Component);

const TRAILERS: &[(&str, &[u8])] = &[("x-checksum", b"abc123"), ("x-parts", b"1")];

async fn echo_with_trailers(path: &str, body: &[u8]) -> EndpointResponse {
    let response = send_with_trailers(path, body, TRAILERS, Ok(()))
        .await
        .expect("send should succeed");
    let response = consume_response(response).await;
    assert!(response.trailers.is_none());
    response
}

impl Guest for Component {
    async fn handle(_request: Request) -> Result<Response, ErrorCode> {
        let response = echo_with_trailers(ECHO_HEADERS, b"ping").await;
        let headers = &response.headers;
        assert_eq!(response.status, 200);
        assert_eq!(echoed_trailer(headers, "x-checksum"), [b"abc123".to_vec()]);
        assert_eq!(echoed_trailer(headers, "x-parts"), [b"1".to_vec()]);

        assert_eq!(
            echoed(headers, "transfer-encoding"),
            [b"chunked".to_vec()],
            "a request carrying trailers must be chunked"
        );
        assert!(
            echoed(headers, "content-length").is_empty(),
            "chunked framing and content-length are mutually exclusive"
        );
        assert_eq!(request_line(headers, "x-request-method"), b"POST");

        assert!(echoed_trailer(headers, "x-absent").is_empty());

        let response = echo_with_trailers(ECHO_BODY, b"chunked-payload").await;
        assert_eq!(response.status, 200);
        assert_eq!(response.body, b"chunked-payload");

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
