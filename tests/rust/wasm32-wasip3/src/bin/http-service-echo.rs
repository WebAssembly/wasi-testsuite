use test_wasm32_wasip3::http::{export, exports::wasi::http::handler::Guest};
use test_wasm32_wasip3::http::{
    wasi::http::types::{ErrorCode, Fields, Method, Request, Response, StatusCode},
    wit_future, wit_stream,
};

struct Component;
export!(Component);

impl Guest for Component {
    async fn handle(request: Request) -> Result<Response, ErrorCode> {
        let method = request.get_method();
        let path = request.get_path_with_query();

        let req_headers = request.get_headers();

        let (_, result_rx) = wit_future::new(|| Ok(()));
        let (body_rx, trailers) = Request::consume_body(request, result_rx);
        let body = body_rx.collect().await;
        let _ = trailers.await;

        let headers = Fields::new();
        let (status, payload): (StatusCode, Option<Vec<u8>>) = match (method, path.as_deref()) {
            (Method::Post, Some("/echo")) => {
                headers
                    .append("content-type", b"application/octet-stream")
                    .unwrap();
                (200, Some(body))
            }
            (Method::Get, Some("/reflect-header")) => {
                if let Some(value) = req_headers.get("x-echo").first() {
                    headers.append("x-echoed", value).unwrap();
                }
                (200, None)
            }
            _ => (404, None),
        };

        let response_body = payload.map(|bytes| {
            headers
                .append("content-length", &bytes.len().to_string().into_bytes())
                .unwrap();
            let (mut body_tx, body_rx) = wit_stream::new();
            wit_bindgen::spawn_local(async move {
                let remaining = body_tx.write_all(bytes).await;
                assert!(remaining.is_empty());
                drop(body_tx);
            });
            body_rx
        });

        let (trailers_tx, trailers_rx) = wit_future::new(|| Ok(None));
        drop(trailers_tx);
        let (response, _sent) = Response::new(headers, response_body, trailers_rx);
        response.set_status_code(status).unwrap();
        Ok(response)
    }
}

fn main() {
    unreachable!("main is a stub");
}
