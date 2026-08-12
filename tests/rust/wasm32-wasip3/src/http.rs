wit_bindgen::generate!({
    inline: r"
	package wasi-testsuite:test;

	world http-test {
	    include wasi:http/service@0.3.0;
	    import wasi:cli/environment@0.3.0;
	}
    ",
    additional_derives: [PartialEq, Eq, Hash, Clone],
    pub_export_macro: true,
    default_bindings_module: "test_wasm32_wasip3::http",
    features:["clocks-timezone"],
    generate_all
});

use wasi::cli::environment;
use wasi::http::client;
use wasi::http::types::{ErrorCode, Fields, Method, Request, Response, Scheme, StatusCode};

fn env_var(name: &str) -> String {
    environment::get_environment()
        .into_iter()
        .find(|(key, _)| key == name)
        .map(|(_, value)| value)
        .unwrap_or_else(|| panic!("{name} must be set by the test runner"))
}

pub fn server_authority(name: &str) -> String {
    env_var(&format!("HTTP_SERVER_{}", name.to_uppercase()))
}

pub fn endpoint_authority() -> String {
    server_authority("main")
}
pub async fn try_send(authority: &str) -> Result<Response, ErrorCode> {
    let (trailers_tx, trailers_rx) = wit_future::new(|| Ok(None));
    drop(trailers_tx);

    let (request, _sent) = Request::new(Fields::new(), None, trailers_rx, None);
    request.set_method(&Method::Get).unwrap();
    request.set_scheme(Some(&Scheme::Http)).unwrap();
    request.set_authority(Some(authority)).unwrap();
    request.set_path_with_query(Some("/")).unwrap();

    client::send(request).await
}

pub struct EndpointResponse {
    pub status: StatusCode,
    pub headers: Vec<(String, Vec<u8>)>,
    pub body: Vec<u8>,
    pub trailers: Option<Vec<(String, Vec<u8>)>>,
}

pub async fn send_with_trailers(
    path: &str,
    body: &[u8],
    trailers: &[(&str, &[u8])],
    outcome: Result<(), ErrorCode>,
) -> Result<Response, ErrorCode> {
    let headers = Fields::new();
    let names: Vec<&str> = trailers.iter().map(|(name, _)| *name).collect();
    if !names.is_empty() {
        headers
            .append("trailer", names.join(", ").as_bytes())
            .unwrap();
    }

    let resolved = outcome.map(|()| {
        let fields = Fields::new();
        for (name, value) in trailers {
            fields.append(name, value).unwrap();
        }
        Some(fields)
    });

    let (mut body_tx, body_rx) = wit_stream::new();
    let (trailers_tx, trailers_rx) = wit_future::new(|| Ok(None));

    let (request, _sent) = Request::new(headers, Some(body_rx), trailers_rx, None);
    request.set_method(&Method::Post).unwrap();
    request.set_scheme(Some(&Scheme::Http)).unwrap();
    request.set_authority(Some(&endpoint_authority())).unwrap();
    request.set_path_with_query(Some(path)).unwrap();

    let payload = body.to_vec();
    wit_bindgen::spawn_local(async move {
        let remaining = body_tx.write_all(payload).await;
        assert!(remaining.is_empty());
        drop(body_tx);
        _ = trailers_tx.write(resolved).await;
    });
    client::send(request).await
}

pub async fn consume_response(response: Response) -> EndpointResponse {
    let status = response.get_status_code();
    let headers = response.get_headers().copy_all();

    let (_, result_rx) = wit_future::new(|| Ok(()));
    let (body_rx, trailers) = Response::consume_body(response, result_rx);
    let body = body_rx.collect().await;
    let trailers = trailers
        .await
        .expect("trailers future should resolve")
        .map(|trailers| trailers.copy_all());

    EndpointResponse {
        status,
        headers,
        body,
        trailers,
    }
}

pub async fn endpoint_request(
    method: &Method,
    path: Option<&str>,
    headers: &[(&str, &[u8])],
) -> EndpointResponse {
    let (trailers_tx, trailers_rx) = wit_future::new(|| Ok(None));
    drop(trailers_tx);

    let fields = Fields::new();
    for (name, value) in headers {
        fields.append(name, value).unwrap();
    }

    let (request, _sent) = Request::new(fields, None, trailers_rx, None);
    request.set_method(method).unwrap();
    request.set_scheme(Some(&Scheme::Http)).unwrap();
    request.set_authority(Some(&endpoint_authority())).unwrap();
    request.set_path_with_query(path).unwrap();

    let response = client::send(request).await.expect("send should succeed");
    consume_response(response).await
}

pub fn echoed(headers: &[(String, Vec<u8>)], name: &str) -> Vec<Vec<u8>> {
    reflected(headers, "x-echo-", name)
}

pub fn echoed_trailer(headers: &[(String, Vec<u8>)], name: &str) -> Vec<Vec<u8>> {
    reflected(headers, "x-trailer-", name)
}

fn reflected(headers: &[(String, Vec<u8>)], prefix: &str, name: &str) -> Vec<Vec<u8>> {
    let wanted = format!("{prefix}{name}");
    headers
        .iter()
        .filter(|(header, _)| header.eq_ignore_ascii_case(&wanted))
        .map(|(_, value)| value.clone())
        .collect()
}

pub fn request_line(headers: &[(String, Vec<u8>)], name: &str) -> Vec<u8> {
    let matches: Vec<_> = headers
        .iter()
        .filter(|(header, _)| header.eq_ignore_ascii_case(name))
        .map(|(_, value)| value.clone())
        .collect();
    assert_eq!(matches.len(), 1, "{name} should be echoed exactly once");
    matches.into_iter().next().unwrap()
}
