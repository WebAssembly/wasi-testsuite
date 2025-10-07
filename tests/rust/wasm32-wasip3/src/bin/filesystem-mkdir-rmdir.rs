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

async fn test_mkdir_rmdir(dir: &Descriptor) {
    let mkdir = |path: &str| dir.create_directory_at(path.to_string());
    let rmdir = |path: &str| dir.remove_directory_at(path.to_string());

    // create-directory-at: async func(path: string) -> result<_, error-code>;
    assert_eq!(dir.create_directory_at("".to_string()).await,
               Err(ErrorCode::NoEntry));
    assert_eq!(mkdir(".").await, Err(ErrorCode::Exist));
    assert_eq!(mkdir("..").await, Err(ErrorCode::NotPermitted));
    assert_eq!(mkdir("parent/foo").await, Err(ErrorCode::NotPermitted));
    assert_eq!(mkdir("/").await, Err(ErrorCode::NotPermitted));
    assert_eq!(
        mkdir("../fs-tests.dir/q.cleanup").await,
        Err(ErrorCode::NotPermitted)
    );
    assert_eq!(
        mkdir("parent/fs-tests.dir/q.cleanup").await,
        Err(ErrorCode::NotPermitted)
    );
    assert_eq!(mkdir("a.txt").await, Err(ErrorCode::Exist));
    mkdir("q.cleanup").await.unwrap();
    assert_eq!(
        rmdir("../fs-tests.dir/q.cleanup").await,
        Err(ErrorCode::NotPermitted)
    );
    assert_eq!(
        rmdir("parent/fs-tests.dir/q.cleanup").await,
        Err(ErrorCode::NotPermitted)
    );
    assert_eq!(rmdir("q.cleanup/").await, Err(ErrorCode::Invalid));
    assert_eq!(
        rmdir("q.cleanup/../../fs-tests.dir/q.cleanup").await,
        Err(ErrorCode::NotPermitted)
    );
    rmdir("q.cleanup").await.unwrap();
    mkdir("q.cleanup/").await.unwrap();
    rmdir("q.cleanup").await.unwrap();
    mkdir("q.cleanup").await.unwrap();
    // FIXME: https://github.com/bytecodealliance/wasmtime/issues/11524
    // rmdir("q.cleanup/")
    //     .await.unwrap();
    // mkdir("q.cleanup/////")
    //     .await.unwrap();
    // rmdir("q.cleanup////////////")
    //     .await.unwrap();
    // Using this instead to clean up:
    rmdir("q.cleanup").await.unwrap();

    // remove-directory-at: async func(path: string) -> result<_, error-code>;
    assert_eq!(rmdir("").await, Err(ErrorCode::NoEntry));
    assert_eq!(rmdir(".").await, Err(ErrorCode::Invalid));
    assert_eq!(rmdir("..").await, Err(ErrorCode::NotPermitted));
    assert_eq!(rmdir("/").await, Err(ErrorCode::NotPermitted));
    assert_eq!(rmdir("a.txt").await, Err(ErrorCode::NotDirectory));
    assert_eq!(rmdir("z.txt").await, Err(ErrorCode::NoEntry));
    assert_eq!(rmdir("parent").await, Err(ErrorCode::NotDirectory));
    assert_eq!(
        rmdir("parent/fs-tests.dir").await,
        Err(ErrorCode::NotPermitted)
    );
}

struct Component;
export!(Component);
impl exports::wasi::cli::run::Guest for Component {
    async fn run() -> Result<(), ()> {
        match &wasi::filesystem::preopens::get_directories()[..] {
            [(dir, dirname)] if dirname == "fs-tests.dir" => {
                test_mkdir_rmdir(dir).await;
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
