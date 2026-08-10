use test_wasm32_wasip3::http::wasi::http::types::{ErrorCode, Fields, Method, Request, Response};
use test_wasm32_wasip3::http::wit_future;
use test_wasm32_wasip3::http::{echoed, endpoint_authority, endpoint_request_with_headers};
use test_wasm32_wasip3::http::{export, exports::wasi::http::handler::Guest, request_line};

const PATH: &str = "/echo-headers";

struct Component;
export!(Component);

fn combined(values: &[Vec<u8>]) -> String {
    values
        .iter()
        .map(|value| String::from_utf8(value.clone()).unwrap())
        .collect::<Vec<_>>()
        .join(", ")
}

impl Guest for Component {
    async fn handle(_request: Request) -> Result<Response, ErrorCode> {
        let (status, headers, body) = endpoint_request_with_headers(
            &Method::Get,
            Some(PATH),
            &[
                ("x-single", b"one"),
                ("x-multi", b"first"),
                ("x-multi", b"second"),
            ],
        )
        .await;
        assert_eq!(status, 200);
        assert!(body.is_empty());

        assert_eq!(echoed(&headers, "x-single"), [b"one".to_vec()]);

        assert_eq!(combined(&echoed(&headers, "x-multi")), "first, second");

        assert_eq!(
            echoed(&headers, "host"),
            [endpoint_authority().into_bytes()],
            "authority should reach the wire as Host"
        );

        // The server reflects the method and path through these headers.
        assert_eq!(request_line(&headers, "x-request-method"), b"GET");
        assert_eq!(request_line(&headers, "x-request-path"), PATH.as_bytes());

        // Headers not sent by the client are not expected.
        assert!(echoed(&headers, "x-absent").is_empty());

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
