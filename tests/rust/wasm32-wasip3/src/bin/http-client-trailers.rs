use test_wasm32_wasip3::http::wasi::http::client;
use test_wasm32_wasip3::http::wasi::http::types::{
    ErrorCode, Fields, Method, Request, Response, Scheme,
};
use test_wasm32_wasip3::http::{echoed, echoed_trailer, endpoint_authority, request_line};
use test_wasm32_wasip3::http::{export, exports::wasi::http::handler::Guest};
use test_wasm32_wasip3::http::{wit_future, wit_stream};

const ECHO_HEADERS: &str = "/echo-headers";
const ECHO_BODY: &str = "/echo-body";

struct Component;
export!(Component);

async fn send_with_trailers(path: &str, body: &[u8]) -> (u16, Vec<(String, Vec<u8>)>, Vec<u8>) {
    let (mut body_tx, body_rx) = wit_stream::new();
    let (trailers_tx, trailers_rx) = wit_future::new(|| Ok(None));

    let headers = Fields::new();
    headers.append("trailer", b"x-checksum, x-parts").unwrap();

    let (request, _sent) = Request::new(headers, Some(body_rx), trailers_rx, None);
    request.set_method(&Method::Post).unwrap();
    request.set_scheme(Some(&Scheme::Http)).unwrap();
    request.set_authority(Some(&endpoint_authority())).unwrap();
    request.set_path_with_query(Some(path)).unwrap();

    let payload = body.to_vec();
    let (_, _, response) = futures::join!(
        async move {
            let remaining = body_tx.write_all(payload).await;
            assert!(remaining.is_empty());
            drop(body_tx);
        },
        async move {
            let trailers = Fields::new();
            trailers.append("x-checksum", b"abc123").unwrap();
            trailers.append("x-parts", b"1").unwrap();
            _ = trailers_tx.write(Ok(Some(trailers))).await;
        },
        client::send(request),
    );
    let response = response.expect("send should succeed");
    let status = response.get_status_code();
    let headers = response.get_headers().copy_all();

    let (_, result_rx) = wit_future::new(|| Ok(()));
    let (body_rx, trailers) = Response::consume_body(response, result_rx);
    let body = body_rx.collect().await;
    assert!(trailers.await.unwrap().is_none());

    (status, headers, body)
}

impl Guest for Component {
    async fn handle(_request: Request) -> Result<Response, ErrorCode> {
        let (status, headers, _) = send_with_trailers(ECHO_HEADERS, b"ping").await;
        assert_eq!(status, 200);
        assert_eq!(echoed_trailer(&headers, "x-checksum"), [b"abc123".to_vec()]);
        assert_eq!(echoed_trailer(&headers, "x-parts"), [b"1".to_vec()]);

        assert_eq!(
            echoed(&headers, "transfer-encoding"),
            [b"chunked".to_vec()],
            "a request carrying trailers must be chunked"
        );
        assert!(
            echoed(&headers, "content-length").is_empty(),
            "chunked framing and content-length are mutually exclusive"
        );
        assert_eq!(request_line(&headers, "x-request-method"), b"POST");

        assert!(echoed_trailer(&headers, "x-absent").is_empty());

        let (status, _, body) = send_with_trailers(ECHO_BODY, b"chunked-payload").await;
        assert_eq!(status, 200);
        assert_eq!(body, b"chunked-payload");

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
