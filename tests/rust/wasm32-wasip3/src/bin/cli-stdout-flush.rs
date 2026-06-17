use test_wasm32_wasip3::cli::{
    export,
    exports::wasi::cli::run::Guest,
    wasi::cli::{stdin, stdout},
    wit_stream,
};

use wit_bindgen::StreamResult;

struct Component;
export!(Component);

impl Guest for Component {
    async fn run() -> Result<(), ()> {
        let (mut tx, rx) = wit_stream::new();
        futures::join!(
            async {
                stdout::write_via_stream(rx).await.unwrap();
            },
            async {
                let remaining = tx.write_all(b"READY".to_vec()).await;
                assert!(remaining.is_empty());

                let (mut stdin, stdin_result) = stdin::read_via_stream();
                let (result, input) = stdin.read(Vec::with_capacity(1)).await;
                assert_eq!(result, StreamResult::Complete(1));
                assert_eq!(input.as_slice(), b"x");

                drop(stdin);
                stdin_result.await.unwrap();
                drop(tx);
            },
        );
        Ok(())
    }
}

fn main() {
    unreachable!();
}
