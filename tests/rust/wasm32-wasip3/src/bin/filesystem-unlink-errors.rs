use std::process;
extern crate wit_bindgen;

wit_bindgen::generate!({
    inline: r"
  package test:test;

  world test {
      include wasi:filesystem/imports@0.3.0-rc-2025-09-16;
      include wasi:cli/command@0.3.0-rc-2025-09-16;
  }
",
    additional_derives: [PartialEq, Eq, Hash, Clone],
    // Work around https://github.com/bytecodealliance/wasm-tools/issues/2285.
    features:["clocks-timezone"],
    generate_all
});

use wasi::filesystem::types::Descriptor;
use wasi::filesystem::types::ErrorCode;

async fn test_unlink_errors(dir: &Descriptor) {
    let rm = |path: &str| dir.unlink_file_at(path.to_string());
    assert_eq!(rm("").await, Err(ErrorCode::NoEntry));
    assert_eq!(rm(".").await, Err(ErrorCode::IsDirectory));
    assert_eq!(rm("..").await, Err(ErrorCode::NotPermitted));
    assert_eq!(rm("../fs-tests.dir").await, Err(ErrorCode::NotPermitted));
    assert_eq!(rm("/").await, Err(ErrorCode::NotPermitted));
    assert_eq!(rm("/etc/passwd").await, Err(ErrorCode::NotPermitted));
    assert_eq!(rm("/etc/passwd").await, Err(ErrorCode::NotPermitted));
    assert_eq!(rm("z.txt").await, Err(ErrorCode::NoEntry));
    assert_eq!(rm("parent/z.txt").await, Err(ErrorCode::NotPermitted));
}

struct Component;
export!(Component);
impl exports::wasi::cli::run::Guest for Component {
    async fn run() -> Result<(), ()> {
        match &wasi::filesystem::preopens::get_directories()[..] {
            [(dir, dirname)] if dirname == "fs-tests.dir" => {
                test_unlink_errors(dir).await;
            }
            [..] => {
                eprintln!("usage: run with one open dir named 'fs-tests.dir'");
                process::exit(1)
            }
        };
        Ok(())
    }
}

fn main() {
    unreachable!("main is a stub");
}
