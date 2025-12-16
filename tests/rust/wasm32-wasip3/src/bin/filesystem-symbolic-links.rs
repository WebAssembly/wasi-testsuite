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
use wasi::filesystem::types::{DescriptorFlags, ErrorCode, OpenFlags, PathFlags};

async fn test_symbolic_links(dir: &Descriptor) {
    // symlink-at: async func(old-path: string, new-path: string) -> result<_, error-code>;
    let ln_s = |from: &str, to: &str| -> _ { dir.symlink_at(from.to_string(), to.to_string()) };
    // readlink-at: async func(path: string) -> result<string, error-code>;
    let readlink = |path: &str| dir.readlink_at(path.to_string());
    let stat_with_flags = |flags: PathFlags, path: &str| dir.stat_at(flags, path.to_string());
    let stat_follow = |path: &str| stat_with_flags(PathFlags::SYMLINK_FOLLOW, path);
    let open_r_follow = |path: &str| -> _ {
        dir.open_at(
            PathFlags::SYMLINK_FOLLOW,
            path.to_string(),
            OpenFlags::empty(),
            DescriptorFlags::READ,
        )
    };
    let open_r = |path: &str| -> _ {
        dir.open_at(
            PathFlags::empty(),
            path.to_string(),
            OpenFlags::empty(),
            DescriptorFlags::READ,
        )
    };
    let rm = |path: &str| dir.unlink_file_at(path.to_string());

    assert_eq!(readlink("").await, Err(ErrorCode::NoEntry));
    assert_eq!(readlink(".").await, Err(ErrorCode::Invalid));
    assert_eq!(readlink("a.txt").await, Err(ErrorCode::Invalid));
    assert_eq!(readlink("z.txt").await, Err(ErrorCode::NoEntry));
    assert_eq!(readlink("./../").await, Err(ErrorCode::NotPermitted));
    assert_eq!(readlink("..").await, Err(ErrorCode::NotPermitted));
    assert_eq!(readlink("/").await, Err(ErrorCode::NotPermitted));
    assert_eq!(readlink("parent").await, Ok("..".to_string()));

    let afd = open_r("a.txt").await.unwrap();
    assert_eq!(
        afd.readlink_at(".".to_string()).await,
        Err(ErrorCode::NotDirectory)
    );

    // https://github.com/WebAssembly/WASI/issues/718
    assert_eq!(
        open_r("parent")
            .await
            .expect_err("open symlink with NOFOLLOW"),
        ErrorCode::Loop
    );

    ln_s("parent", "parent-link").await.unwrap();
    assert_eq!(open_r("parent-link").await.unwrap_err(), ErrorCode::Loop);
    assert_eq!(
        open_r_follow("parent-link").await.unwrap_err(),
        ErrorCode::NotPermitted
    );
    assert_eq!(
        stat_follow("parent-link").await.unwrap_err(),
        ErrorCode::NotPermitted
    );
    assert_eq!(open_r("parent-link").await.unwrap_err(), ErrorCode::Loop);
    assert_eq!(
        ln_s("a.txt", "parent-link/a.txt").await,
        Err(ErrorCode::NotPermitted)
    );
    rm("parent-link").await.unwrap();

    ln_s("self", "self").await.unwrap();
    assert_eq!(open_r_follow("self").await.unwrap_err(), ErrorCode::Loop);
    assert_eq!(stat_follow("self").await.unwrap_err(), ErrorCode::Loop);
    rm("self").await.unwrap();

    assert_eq!(ln_s("whatever", "").await, Err(ErrorCode::NoEntry));
    assert_eq!(ln_s("", "whatever").await, Err(ErrorCode::NoEntry));

    ln_s("..\\.", "parent-link").await.unwrap();
    assert_eq!(open_r("parent-link").await.unwrap_err(), ErrorCode::Loop);
    match open_r_follow("parent-link/fs-tests.dir").await {
        // Backslashes are not separators.
        Err(ErrorCode::NoEntry) => (),
        // Backslashes are separators.
        Err(ErrorCode::NotPermitted) => {
            assert_eq!(
                stat_follow("parent-link").await.unwrap_err(),
                ErrorCode::NotPermitted
            );
            assert_eq!(
                open_r("parent-link/fs-tests.dir/a.txt").await.unwrap_err(),
                ErrorCode::NotPermitted
            );
            assert_eq!(
                ln_s("a.txt", "parent-link/fs-tests.dir/q.txt").await,
                Err(ErrorCode::NotPermitted)
            );
        }
        Err(e) => panic!("unexpected error: {}", e),
        Ok(_) => panic!("unexpected success"),
    }
    rm("parent-link").await.unwrap();

    ln_s("..\\fs-tests.dir", "self-link").await.unwrap();
    assert_eq!(open_r("self-link").await.unwrap_err(), ErrorCode::Loop);
    match open_r_follow("self-link").await {
        // Backslashes are not separators.
        Err(ErrorCode::NoEntry) => (),
        // Backslashes are separators.
        Err(ErrorCode::NotPermitted) => {
            assert_eq!(
                stat_follow("self-link").await.unwrap_err(),
                ErrorCode::NotPermitted
            );
            assert_eq!(
                open_r("self-link/a.txt").await.unwrap_err(),
                ErrorCode::NotPermitted
            );
            assert_eq!(
                ln_s("a.txt", "self-link/q.txt").await,
                Err(ErrorCode::NotPermitted)
            );
        }
        Err(e) => panic!("unexpected error: {}", e),
        Ok(_) => panic!("unexpected success"),
    }
    rm("self-link").await.unwrap();
}

struct Component;
export!(Component);
impl exports::wasi::cli::run::Guest for Component {
    async fn run() -> Result<(), ()> {
        match &wasi::filesystem::preopens::get_directories()[..] {
            [(dir, dirname)] if dirname == "fs-tests.dir" => {
                test_symbolic_links(dir).await;
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
