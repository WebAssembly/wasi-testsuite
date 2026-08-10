use test_wasm32_wasip3::http::wasi::http::types::{ErrorCode, Fields, Request, Response};
use test_wasm32_wasip3::http::wit_future;
use test_wasm32_wasip3::http::{endpoint_authority, server_authority, try_send};
use test_wasm32_wasip3::http::{export, exports::wasi::http::handler::Guest};

struct Component;
export!(Component);

impl Guest for Component {
    async fn handle(_request: Request) -> Result<Response, ErrorCode> {
        let response = try_send(&endpoint_authority())
            .await
            .expect("send to a live endpoint should succeed");
        assert_eq!(response.get_status_code(), 200);
        drop(response);

        try_send(&server_authority("dead"))
            .await
            .expect_err("send to a closed port should fail");

        try_send("nonexistent.invalid:80")
            .await
            .expect_err("send to an unresolvable authority should fail");

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
