use test_wasm32_wasip3::http::send_with_trailers;
use test_wasm32_wasip3::http::wasi::http::types::{ErrorCode, Fields, Request, Response};
use test_wasm32_wasip3::http::wit_future;
use test_wasm32_wasip3::http::{export, exports::wasi::http::handler::Guest};

const ECHO_BODY: &str = "/echo-body";
const BODY: &[u8] = b"partial";
const TRAILERS: &[(&str, &[u8])] = &[("x-checksum", b"abc123")];

struct Component;
export!(Component);

impl Guest for Component {
    async fn handle(_request: Request) -> Result<Response, ErrorCode> {
        let response = send_with_trailers(ECHO_BODY, BODY, TRAILERS, Ok(()))
            .await
            .expect("send should succeed when the trailers resolve");
        assert_eq!(response.get_status_code(), 200);

        let aborted = send_with_trailers(
            ECHO_BODY,
            BODY,
            TRAILERS,
            Err(ErrorCode::InternalError(None)),
        )
        .await;
        assert!(
            aborted.is_err(),
            "a request whose trailers resolve to an error must not produce a response"
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
