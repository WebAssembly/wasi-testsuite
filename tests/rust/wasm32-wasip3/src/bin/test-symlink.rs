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

async fn test_symlink() {
    match &wasi::filesystem::preopens::get_directories()[..] {
        [(dir, _)] => {
            dir.create_directory_at("child.cleanup".to_string())
                .await
                .unwrap();
            dir.symlink_at("../a.txt".to_string(), "child.cleanup/b".to_string())
                .await
                .unwrap();
        }
        [..] => {
            eprintln!("usage: run with one open dir");
            process::exit(1)
        }
    }
}

struct Component;
export!(Component);
impl exports::wasi::cli::run::Guest for Component {
    async fn run() -> Result<(), ()> {
        test_symlink().await;
        Ok(())
    }
}

fn main() {
    unreachable!("main is a stub");
}
