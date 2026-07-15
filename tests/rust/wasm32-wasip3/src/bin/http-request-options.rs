use test_wasm32_wasip3::cli::{export, exports::wasi::cli::run::Guest};
use test_wasm32_wasip3::http::{
    wasi::http::types::{Fields, Request, RequestOptions, RequestOptionsError},
    wit_future,
};

const CONNECT: u64 = 1_000_000;
const FIRST_BYTE: u64 = 2_000_000;
const BETWEEN_BYTES: u64 = 3_000_000;

fn test_default_values() {
    let options = RequestOptions::new();
    assert_eq!(options.get_connect_timeout(), None);
    assert_eq!(options.get_first_byte_timeout(), None);
    assert_eq!(options.get_between_bytes_timeout(), None);
}

fn test_set_get_roundtrip() {
    let options = RequestOptions::new();

    options.set_connect_timeout(Some(CONNECT)).unwrap();
    assert_eq!(options.get_connect_timeout(), Some(CONNECT));

    options.set_first_byte_timeout(Some(FIRST_BYTE)).unwrap();
    assert_eq!(options.get_first_byte_timeout(), Some(FIRST_BYTE));

    options
        .set_between_bytes_timeout(Some(BETWEEN_BYTES))
        .unwrap();
    assert_eq!(options.get_between_bytes_timeout(), Some(BETWEEN_BYTES));

    options.set_connect_timeout(None).unwrap();
    assert_eq!(options.get_connect_timeout(), None);
}

fn test_clone_independence() {
    let original = RequestOptions::new();
    original.set_connect_timeout(Some(CONNECT)).unwrap();

    let clone = original.clone();
    assert_eq!(clone.get_connect_timeout(), Some(CONNECT));

    clone.set_connect_timeout(Some(FIRST_BYTE)).unwrap();
    assert_eq!(clone.get_connect_timeout(), Some(FIRST_BYTE));
    assert_eq!(original.get_connect_timeout(), Some(CONNECT));
}

fn test_request_get_options() {
    let options = RequestOptions::new();
    options.set_connect_timeout(Some(CONNECT)).unwrap();

    let (_, trailers_rx) = wit_future::new(|| Ok(None));
    let (request, _sent) = Request::new(Fields::new(), None, trailers_rx, Some(options));

    let got = request
        .get_options()
        .expect("options passed to `new` should be retrievable");
    assert_eq!(got.get_connect_timeout(), Some(CONNECT));

    assert_eq!(
        got.set_connect_timeout(Some(FIRST_BYTE)),
        Err(RequestOptionsError::Immutable)
    );
    assert_eq!(
        got.set_first_byte_timeout(Some(FIRST_BYTE)),
        Err(RequestOptionsError::Immutable)
    );
    assert_eq!(
        got.set_between_bytes_timeout(Some(BETWEEN_BYTES)),
        Err(RequestOptionsError::Immutable)
    );
}

fn test_request_no_options() {
    let (_, trailers_rx) = wit_future::new(|| Ok(None));
    let (request, _sent) = Request::new(Fields::new(), None, trailers_rx, None);
    assert!(request.get_options().is_none());
}

struct Component;
export!(Component);

impl Guest for Component {
    async fn run() -> Result<(), ()> {
        test_default_values();
        test_set_get_roundtrip();
        test_clone_independence();
        test_request_get_options();
        test_request_no_options();
        Ok(())
    }
}

fn main() {
    unreachable!("main is a stub");
}
