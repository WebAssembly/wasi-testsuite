use test_wasm32_wasip3::http::endpoint_authority;
use test_wasm32_wasip3::http::wasi::http::client;
use test_wasm32_wasip3::http::wasi::http::types::{
    ErrorCode, Fields, Method, Request, Response, Scheme,
};
use test_wasm32_wasip3::http::{export, exports::wasi::http::handler::Guest};
use test_wasm32_wasip3::http::{wit_future, wit_stream};

async fn read_body(response: Response) -> Vec<u8> {
    let (_, result_rx) = wit_future::new(|| Ok(()));
    let (body_rx, trailers) = Response::consume_body(response, result_rx);
    let body = body_rx.collect().await;
    assert!(trailers.await.unwrap().is_none());
    body
}

struct Component;
export!(Component);

impl Guest for Component {
    async fn handle(_request: Request) -> Result<Response, ErrorCode> {
        let authority = endpoint_authority();
        let payload = b"ping".to_vec();

        let headers = Fields::new();
        headers
            .append("content-length", payload.len().to_string().as_bytes())
            .unwrap();

        let (mut body_tx, body_rx) = wit_stream::new();
        let sent_bytes = payload.clone();
        wit_bindgen::spawn_local(async move {
            let remaining = body_tx.write_all(sent_bytes).await;
            assert!(remaining.is_empty());
            drop(body_tx);
        });

        let (trailers_tx, trailers_rx) = wit_future::new(|| Ok(None));
        drop(trailers_tx);

        let (request, _sent) = Request::new(headers, Some(body_rx), trailers_rx, None);
        request.set_method(&Method::Post).unwrap();
        request.set_scheme(Some(&Scheme::Http)).unwrap();
        request.set_authority(Some(&authority)).unwrap();
        request.set_path_with_query(Some("/echo")).unwrap();

        let response = client::send(request).await.expect("send should succeed");
        assert_eq!(
            read_body(response).await,
            payload,
            "endpoint must echo the body"
        );

        let headers = Fields::new();
        let (trailers_tx, trailers_rx) = wit_future::new(|| Ok(None));
        drop(trailers_tx);
        let (response, _sent) = Response::new(headers, None, trailers_rx);
        response.set_status_code(200).unwrap();
        Ok(response)
    }
}

fn main() {
    unreachable!("main is a stub");
}
