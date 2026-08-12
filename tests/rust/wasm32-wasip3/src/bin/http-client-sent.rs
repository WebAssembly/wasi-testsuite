use test_wasm32_wasip3::http::wasi::http::client;
use test_wasm32_wasip3::http::wasi::http::types::{
    ErrorCode, Fields, Method, Request, Response, Scheme,
};
use test_wasm32_wasip3::http::wit_future;
use test_wasm32_wasip3::http::{export, exports::wasi::http::handler::Guest};

struct Component;
export!(Component);

impl Guest for Component {
    async fn handle(_request: Request) -> Result<Response, ErrorCode> {
        // See https://github.com/bytecodealliance/wasmtime/issues/14112.
        let (trailers_tx, trailers_rx) = wit_future::new(|| Ok(None));
        drop(trailers_tx);

        let (request, sent) = Request::new(Fields::new(), None, trailers_rx, None);
        request.set_method(&Method::Get).unwrap();
        request.set_scheme(Some(&Scheme::Http)).unwrap();
        request
            .set_authority(Some("nonexistent.invalid:80"))
            .unwrap();
        request.set_path_with_query(Some("/")).unwrap();

        client::send(request)
            .await
            .expect_err("send to an unresolvable authority should fail");
        assert!(
            sent.await.is_err(),
            "a request that was never transmitted must not report successful transmission"
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
