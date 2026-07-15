use test_wasm32_wasip3::http::{export, exports::wasi::http::handler::Guest};
use test_wasm32_wasip3::http::{
    wasi::http::types::{ErrorCode, Fields, Request, Response},
    wit_future,
};

struct Component;
export!(Component);

impl Guest for Component {
    async fn handle(request: Request) -> Result<Response, ErrorCode> {
        assert!(request.get_scheme().is_some(), "expected scheme to be set");
        assert!(
            request.get_authority().is_some(),
            "expected authority to be set"
        );

        let (_, result_rx) = wit_future::new(|| Ok(()));
        let (body_rx, trailers) = Request::consume_body(request, result_rx);
        let _ = body_rx.collect().await;
        let _ = trailers.await;

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
