use std::process;
extern crate wit_bindgen;

wit_bindgen::generate!({
    inline: r"
  package test:test;

  world test {
      include wasi:filesystem/imports@0.3.0-rc-2025-08-15;
      include wasi:cli/command@0.3.0-rc-2025-08-15;
  }
",
    additional_derives: [PartialEq, Eq, Hash, Clone],
    // Work around https://github.com/bytecodealliance/wasm-tools/issues/2285.
    features:["clocks-timezone"],
    async: [
        "wasi:cli/run@0.3.0-rc-2025-08-15#run",
    ],
    generate_all
});

use wasi::clocks::wall_clock::Datetime;
use wasi::filesystem::types::Descriptor;
use wasi::filesystem::types::{Advice, DirectoryEntry, NewTimestamp};
use wasi::filesystem::types::{DescriptorFlags, ErrorCode, OpenFlags, PathFlags};
use wasi::filesystem::types::{DescriptorStat, DescriptorType};
use wit_bindgen::StreamResult;

fn check_timestamp(t: Datetime) {
    assert!(t.nanoseconds < 1_000_000_000);
}

fn check_stat(stat: &DescriptorStat, type_: DescriptorType) {
    assert_eq!(stat.type_, type_);
    // assert_eq!(stat.link_count, 0) ?
    // assert_eq!(stat.size, 0) ?
    if let Some(t) = stat.data_access_timestamp {
        check_timestamp(t)
    };
    if let Some(t) = stat.data_modification_timestamp {
        check_timestamp(t)
    };
    if let Some(t) = stat.status_change_timestamp {
        check_timestamp(t)
    }
}

async fn check_metadata_hash(a: &Descriptor, b: &Descriptor) {
    let a_hash = a.metadata_hash().await;
    let b_hash = b.metadata_hash().await;
    if a_hash.is_ok() && a_hash == b_hash {
        assert_eq!(a.stat().await.unwrap(), b.stat().await.unwrap());
    }
}

async fn check_metadata_hash_at(
    a: &Descriptor,
    a_flags: PathFlags,
    a_name: &str,
    b: &Descriptor,
    b_flags: PathFlags,
    b_name: &str,
) {
    let a_hash = a.metadata_hash_at(a_flags, a_name.to_string()).await;
    let b_hash = b.metadata_hash_at(b_flags, b_name.to_string()).await;
    if a_hash.is_ok() && a_hash == b_hash {
        assert_eq!(
            a.stat_at(a_flags, a_name.to_string()).await.unwrap(),
            b.stat_at(b_flags, b_name.to_string()).await.unwrap()
        );
    }
}

async fn check_test_harness(dir: &Descriptor) {
    let stat = |path: &str| -> _ { dir.stat_at(PathFlags::empty(), path.to_string()) };

    check_stat(
        &stat("a.txt").await.expect("expected fs-tests.dir/a.txt"),
        DescriptorType::RegularFile,
    );
    check_stat(
        &stat("b.txt").await.expect("expected fs-tests.dir/b.txt"),
        DescriptorType::RegularFile,
    );
    check_stat(
        &stat("parent")
            .await
            .expect("expected symlink fs-test.dir/parent"),
        DescriptorType::SymbolicLink,
    );
}

async fn test_mkdir_rmdir(dir: &Descriptor) {
    let mkdir = |path: &str| dir.create_directory_at(path.to_string());
    let rmdir = |path: &str| dir.remove_directory_at(path.to_string());

    // create-directory-at: async func(path: string) -> result<_, error-code>;
    // FIXME: https://github.com/bytecodealliance/wasmtime/issues/11607
    // assert_eq!(dir.create_directory_at("".to_string()).await,
    //            Err(ErrorCode::Invalid));
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
    // FIXME: https://github.com/bytecodealliance/wasmtime/issues/11607
    // assert_eq!(rmdir("").await,
    //            Err(ErrorCode::Invalid));
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

async fn test_stat(dir: &Descriptor) {
    let afd = dir
        .open_at(
            PathFlags::empty(),
            "a.txt".to_string(),
            OpenFlags::empty(),
            DescriptorFlags::READ,
        )
        .await
        .unwrap();
    let bfd = dir
        .open_at(
            PathFlags::empty(),
            "b.txt".to_string(),
            OpenFlags::empty(),
            DescriptorFlags::READ,
        )
        .await
        .unwrap();
    let stat_with_flags = |flags: PathFlags, path: &str| dir.stat_at(flags, path.to_string());
    let stat = |path: &str| stat_with_flags(PathFlags::empty(), path);
    let stat_follow = |path: &str| stat_with_flags(PathFlags::SYMLINK_FOLLOW, path);

    // stat: async func() -> result<descriptor-stat, error-code>;
    check_stat(&dir.stat().await.unwrap(), DescriptorType::Directory);
    check_stat(&afd.stat().await.unwrap(), DescriptorType::RegularFile);
    check_stat(&bfd.stat().await.unwrap(), DescriptorType::RegularFile);

    // stat-at: async func(path-flags: path-flags, path: string) -> result<descriptor-stat, error-code>;
    assert_eq!(
        afd.stat_at(PathFlags::empty(), "z.txt".to_string()).await,
        Err(ErrorCode::NotDirectory)
    );
    assert_eq!(
        afd.stat_at(PathFlags::empty(), ".".to_string()).await,
        Err(ErrorCode::NotDirectory)
    );

    // FIXME: https://github.com/bytecodealliance/wasmtime/issues/11607
    // assert_eq!(stat("".to_string()).await,
    //            Err(ErrorCode::Invalid));
    assert_eq!(stat("..").await, Err(ErrorCode::NotPermitted));
    assert_eq!(stat_follow("parent").await, Err(ErrorCode::NotPermitted));
    assert_eq!(
        stat_follow("parent/fs-tests.dir").await,
        Err(ErrorCode::NotPermitted)
    );
    assert_eq!(stat(".").await, dir.stat().await);
    // FIXME: https://github.com/bytecodealliance/wasmtime/issues/11606
    // assert_eq!(stat_at("/").await,
    //            Err(ErrorCode::NotPermitted));
    assert_eq!(stat("/etc/passwd").await, Err(ErrorCode::NotPermitted));
    assert_eq!(stat("z.txt").await, Err(ErrorCode::NoEntry));

    // set-times-at: async func(path-flags: path-flags, path: string, data-access-timestamp: new-timestamp, data-modification-timestamp: new-timestamp) -> result<_, error-code>;
    {
        let atime = Datetime {
            seconds: 42,
            nanoseconds: 0,
        };
        let mtime = Datetime {
            seconds: 69,
            nanoseconds: 0,
        };
        assert_eq!(
            dir.set_times_at(
                PathFlags::empty(),
                "z.txt".to_string(),
                NewTimestamp::Timestamp(atime),
                NewTimestamp::Timestamp(mtime)
            )
            .await,
            Err(ErrorCode::NoEntry)
        );
        // FIXME: https://github.com/bytecodealliance/wasmtime/issues/11607
        // assert_eq!(dir.set_times_at(PathFlags::empty(),
        //                             "".to_string(),
        //                             NewTimestamp::Timestamp(atime),
        //                             NewTimestamp::Timestamp(mtime)).await,
        //            Err(ErrorCode::Invalid));
        assert_eq!(
            dir.set_times_at(
                PathFlags::empty(),
                "/".to_string(),
                NewTimestamp::Timestamp(atime),
                NewTimestamp::Timestamp(mtime)
            )
            .await,
            Err(ErrorCode::NotPermitted)
        );
        assert_eq!(
            dir.set_times_at(
                PathFlags::empty(),
                "..".to_string(),
                NewTimestamp::Timestamp(atime),
                NewTimestamp::Timestamp(mtime)
            )
            .await,
            Err(ErrorCode::NotPermitted)
        );
        assert_eq!(
            dir.set_times_at(
                PathFlags::SYMLINK_FOLLOW,
                "parent".to_string(),
                NewTimestamp::Timestamp(atime),
                NewTimestamp::Timestamp(mtime)
            )
            .await,
            Err(ErrorCode::NotPermitted)
        );
        assert_eq!(
            dir.set_times_at(
                PathFlags::empty(),
                "../foo".to_string(),
                NewTimestamp::Timestamp(atime),
                NewTimestamp::Timestamp(mtime)
            )
            .await,
            Err(ErrorCode::NotPermitted)
        );
        assert_eq!(
            dir.set_times_at(
                PathFlags::SYMLINK_FOLLOW,
                "parent/foo".to_string(),
                NewTimestamp::Timestamp(atime),
                NewTimestamp::Timestamp(mtime)
            )
            .await,
            Err(ErrorCode::NotPermitted)
        );
    }

    if let Some(atime) = afd.stat().await.unwrap().data_access_timestamp {
        let mtime = afd
            .stat()
            .await
            .unwrap()
            .data_modification_timestamp
            .unwrap();
        let new_atime = Datetime {
            seconds: 42,
            nanoseconds: 0,
        };
        let new_mtime = Datetime {
            seconds: 69,
            nanoseconds: 0,
        };
        assert_eq!(
            dir.set_times_at(
                PathFlags::empty(),
                "a.txt".to_string(),
                NewTimestamp::Timestamp(new_atime),
                NewTimestamp::Timestamp(new_mtime)
            )
            .await,
            Ok(())
        );
        assert_eq!(
            afd.stat().await.unwrap().data_access_timestamp,
            Some(new_atime)
        );
        assert_eq!(
            afd.stat().await.unwrap().data_modification_timestamp,
            Some(new_mtime)
        );
        assert_eq!(
            dir.set_times_at(
                PathFlags::empty(),
                "a.txt".to_string(),
                NewTimestamp::Timestamp(atime),
                NewTimestamp::Timestamp(mtime)
            )
            .await,
            Ok(())
        );
        assert_eq!(afd.stat().await.unwrap().data_access_timestamp, Some(atime));
        assert_eq!(
            afd.stat().await.unwrap().data_modification_timestamp,
            Some(mtime)
        );

        // set-times: async func(data-access-timestamp: new-timestamp, data-modification-timestamp: new-timestamp) -> result<_, error-code>;
        assert_eq!(
            afd.set_times(
                NewTimestamp::Timestamp(new_atime),
                NewTimestamp::Timestamp(new_mtime)
            )
            .await,
            Ok(())
        );
        assert_eq!(
            afd.stat().await.unwrap().data_access_timestamp,
            Some(new_atime)
        );
        assert_eq!(
            afd.stat().await.unwrap().data_modification_timestamp,
            Some(new_mtime)
        );
        assert_eq!(
            afd.set_times(
                NewTimestamp::Timestamp(atime),
                NewTimestamp::Timestamp(mtime)
            )
            .await,
            Ok(())
        );
        assert_eq!(afd.stat().await.unwrap().data_access_timestamp, Some(atime));
        assert_eq!(
            afd.stat().await.unwrap().data_modification_timestamp,
            Some(mtime)
        );
    }

    // set-times: async func(data-access-timestamp: new-timestamp, data-modification-timestamp: new-timestamp) -> result<_, error-code>;
    // TODO.
}

async fn test_hard_links(dir: &Descriptor) {
    let ln_with_flags = |flags: PathFlags, from: &str, to: &str| -> _ {
        dir.link_at(flags, from.to_string(), dir, to.to_string())
    };
    let ln = |from: &str, to: &str| -> _ { ln_with_flags(PathFlags::empty(), from, to) };
    let _ln_follow =
        |from: &str, to: &str| -> _ { ln_with_flags(PathFlags::SYMLINK_FOLLOW, from, to) };
    let rm = |path: &str| dir.unlink_file_at(path.to_string());
    let mkdir = |path: &str| dir.create_directory_at(path.to_string());
    let rmdir = |path: &str| dir.remove_directory_at(path.to_string());

    // link-at: async func(old-path-flags: path-flags, old-path: string, new-descriptor: borrow<descriptor>, new-path: string) -> result<_, error-code>;
    assert_eq!(ln(".", "foo").await, Err(ErrorCode::NotPermitted));
    // FIXME: https://github.com/bytecodealliance/wasmtime/issues/11607
    // assert_eq!(ln("", "foo").await,
    //            Err(ErrorCode::NoEntry));
    // assert_eq!(ln("", "").await,
    //            Err(ErrorCode::NoEntry));
    // assert_eq!(ln("a.txt", "").await,
    //            Err(ErrorCode::NoEntry));
    assert_eq!(ln("a.txt", "a.txt").await, Err(ErrorCode::Exist));
    assert_eq!(ln("/", "a.txt").await, Err(ErrorCode::NotPermitted));
    assert_eq!(ln("a.txt", "/").await, Err(ErrorCode::NotPermitted));
    assert_eq!(ln("a.txt", "/a.txt").await, Err(ErrorCode::NotPermitted));
    assert_eq!(ln("..", "a.txt").await, Err(ErrorCode::NotPermitted));
    assert_eq!(ln("a.txt", "..").await, Err(ErrorCode::NotPermitted));
    // FIXME: https://github.com/bytecodealliance/wasmtime/issues/11607
    // assert_eq!(ln_follow("parent/foo", "a.txt").await,
    //            Err(ErrorCode::NotPermitted));
    // assert_eq!(ln_follow("a.txt", "parent/foo").await,
    //            Err(ErrorCode::NotPermitted));
    ln("a.txt", "c.cleanup").await.unwrap();
    rm("c.cleanup").await.unwrap();
    mkdir("d.cleanup").await.unwrap();
    ln("a.txt", "d.cleanup/q.txt").await.unwrap();
    rm("d.cleanup/q.txt").await.unwrap();
    assert_eq!(
        ln("d.cleanup", "e.cleanup").await,
        // https://github.com/WebAssembly/wasi-filesystem/issues/184
        Err(ErrorCode::NotPermitted)
    );
    rmdir("d.cleanup").await.unwrap();
}

async fn test_rename(dir: &Descriptor) {
    // rename-at: async func(old-path: string, new-descriptor: borrow<descriptor>, new-path: string) -> result<_, error-code>;
    let mv = |from: &str, to: &str| -> _ { dir.rename_at(from.to_string(), dir, to.to_string()) };
    let ln_s = |from: &str, to: &str| -> _ { dir.symlink_at(from.to_string(), to.to_string()) };

    mv("a.txt", "a.txt").await.unwrap();
    ln_s("a.txt", "c.cleanup").await.unwrap();
    mv("a.txt", "c.cleanup").await.unwrap();
    assert_eq!(mv("a.txt", "a.txt").await, Err(ErrorCode::NoEntry));
    mv("c.cleanup", "a.txt").await.unwrap();
    assert_eq!(mv("c.cleanup", "a.txt").await, Err(ErrorCode::NoEntry));
    assert_eq!(
        mv("does-not-exist.txt", "q.txt").await,
        Err(ErrorCode::NoEntry)
    );
    match mv(".", "q.txt").await {
        Err(ErrorCode::Busy) => {}
        Err(ErrorCode::Invalid) => {}
        Ok(()) => {
            panic!("mv . q.txt unexpectedly succeeded");
        }
        Err(err) => {
            panic!("mv . q.txt: unexpected error {}", err);
        }
    };
    mv("a.txt", "c.cleanup").await.unwrap();
    assert_eq!(mv("a.txt", "q.txt").await, Err(ErrorCode::NoEntry));
    mv("c.cleanup", "a.txt").await.unwrap();
    assert_eq!(mv("a.txt", "../q.txt").await, Err(ErrorCode::NotPermitted));
    assert_eq!(
        mv("a.txt", "parent/q.txt").await,
        Err(ErrorCode::NotPermitted)
    );
    assert_eq!(
        mv("a.txt", "/tmp/q.txt").await,
        Err(ErrorCode::NotPermitted)
    );
}

async fn test_symbolic_links(dir: &Descriptor) {
    let ln_s = |from: &str, to: &str| -> _ { dir.symlink_at(from.to_string(), to.to_string()) };
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

    // readlink-at: async func(path: string) -> result<string, error-code>;
    // FIXME: https://github.com/bytecodealliance/wasmtime/issues/11607
    // assert_eq!(readlink("").await,
    //            Err(ErrorCode::Invalid));
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

    // https://github.com/WebAssembly/wasi-filesystem/issues/186
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
    // symlink-at: async func(old-path: string, new-path: string) -> result<_, error-code>;
}

async fn test_is_same_object(dir: &Descriptor) {
    let afd = dir
        .open_at(
            PathFlags::empty(),
            "a.txt".to_string(),
            OpenFlags::empty(),
            DescriptorFlags::READ,
        )
        .await
        .unwrap();
    let bfd = dir
        .open_at(
            PathFlags::empty(),
            "b.txt".to_string(),
            OpenFlags::empty(),
            DescriptorFlags::READ,
        )
        .await
        .unwrap();

    // is-same-object: async func(other: borrow<descriptor>) -> bool;
    assert!(dir.is_same_object(dir).await);
    {
        let other = dir
            .open_at(
                PathFlags::empty(),
                ".".to_string(),
                OpenFlags::empty(),
                DescriptorFlags::READ,
            )
            .await
            .unwrap();
        assert!(dir.is_same_object(&other).await);
    }
    assert!(!dir.is_same_object(&afd).await);
    assert!(afd.is_same_object(&afd).await);
    assert!(!afd.is_same_object(&bfd).await);
    assert!(bfd.is_same_object(&bfd).await);
}

async fn test_metadata_hash(dir: &Descriptor) {
    let afd = dir
        .open_at(
            PathFlags::empty(),
            "a.txt".to_string(),
            OpenFlags::empty(),
            DescriptorFlags::READ,
        )
        .await
        .unwrap();
    let bfd = dir
        .open_at(
            PathFlags::empty(),
            "b.txt".to_string(),
            OpenFlags::empty(),
            DescriptorFlags::READ,
        )
        .await
        .unwrap();

    // metadata-hash: async func() -> result<metadata-hash-value, error-code>;
    check_metadata_hash(&dir, &dir).await;
    check_metadata_hash(&dir, &afd).await;
    check_metadata_hash(&afd, &afd).await;
    check_metadata_hash(&afd, &bfd).await;

    // metadata-hash-at: async func(path-flags: path-flags, path: string) -> result<metadata-hash-value, error-code>;
    // FIXME: https://github.com/bytecodealliance/wasmtime/issues/11606
    // assert_eq!(dir.metadata_hash_at(PathFlags::empty(), "/".to_string()).await,
    //            Err(ErrorCode::NotPermitted));
    // FIXME: https://github.com/bytecodealliance/wasmtime/issues/11607
    // assert_eq!(dir.metadata_hash_at(PathFlags::empty(), "".to_string()).await,
    //            Err(ErrorCode::Invalid));
    assert_eq!(
        dir.metadata_hash_at(PathFlags::empty(), "/etc/passwd".to_string())
            .await,
        Err(ErrorCode::NotPermitted)
    );
    assert_eq!(
        dir.metadata_hash_at(PathFlags::empty(), "/does-not-exist".to_string())
            .await,
        Err(ErrorCode::NotPermitted)
    );
    check_metadata_hash_at(dir, PathFlags::empty(), ".", dir, PathFlags::empty(), ".").await;
    check_metadata_hash_at(
        dir,
        PathFlags::empty(),
        "a.txt",
        dir,
        PathFlags::empty(),
        ".",
    )
    .await;
    check_metadata_hash_at(
        dir,
        PathFlags::empty(),
        "a.txt",
        dir,
        PathFlags::empty(),
        "a.txt",
    )
    .await;
    check_metadata_hash_at(
        dir,
        PathFlags::empty(),
        "a.txt",
        dir,
        PathFlags::empty(),
        "b.txt",
    )
    .await;
}

async fn test_open_errors(dir: &Descriptor) {
    let open = |flags: PathFlags, path: &str| -> _ {
        dir.open_at(
            flags,
            path.to_string(),
            OpenFlags::empty(),
            DescriptorFlags::READ,
        )
    };
    let open_r = |path: &str| open(PathFlags::empty(), path);
    let open_r_follow = |path: &str| open(PathFlags::SYMLINK_FOLLOW, path);
    // open-at: async func(path-flags: path-flags, path: string, open-flags: open-flags, %flags: descriptor-flags) -> result<descriptor, error-code>;
    // FIXME: https://github.com/bytecodealliance/wasmtime/issues/11607
    // assert_eq!(dir.open_at(PathFlags::empty(), "".to_string(),
    //                          OpenFlags::empty(), DescriptorFlags::READ)
    //            .await.expect_err("open"),
    //            ErrorCode::Invalid);
    assert_eq!(
        open_r("..").await.expect_err("open .."),
        ErrorCode::NotPermitted
    );
    assert_eq!(
        open_r_follow("parent").await.expect_err("open parent"),
        ErrorCode::NotPermitted
    );
    assert_eq!(
        open_r("/").await.expect_err("open /"),
        ErrorCode::NotPermitted
    );
}

async fn test_unlink_errors(dir: &Descriptor) {
    let rm = |path: &str| dir.unlink_file_at(path.to_string());
    // FIXME: https://github.com/bytecodealliance/wasmtime/issues/11607
    // assert_eq!(rm("").await,
    //            Err(ErrorCode::Invalid));
    assert_eq!(rm(".").await, Err(ErrorCode::IsDirectory));
    assert_eq!(rm("..").await, Err(ErrorCode::NotPermitted));
    assert_eq!(rm("../fs-tests.dir").await, Err(ErrorCode::NotPermitted));
    assert_eq!(rm("/").await, Err(ErrorCode::NotPermitted));
    assert_eq!(rm("/etc/passwd").await, Err(ErrorCode::NotPermitted));
    assert_eq!(rm("/etc/passwd").await, Err(ErrorCode::NotPermitted));
    assert_eq!(rm("z.txt").await, Err(ErrorCode::NoEntry));
    assert_eq!(rm("parent/z.txt").await, Err(ErrorCode::NotPermitted));
}

async fn test_advise(dir: &Descriptor) {
    // Advise should fail on directories.
    assert_eq!(
        dir.advise(0, 0, Advice::Normal).await,
        Err(ErrorCode::BadDescriptor)
    );

    let fd = dir
        .open_at(
            PathFlags::empty(),
            "a.txt".to_string(),
            OpenFlags::empty(),
            DescriptorFlags::READ,
        )
        .await
        .unwrap();

    let size = fd.stat().await.unwrap().size;
    for advice in [
        Advice::Normal,
        Advice::Sequential,
        Advice::Random,
        Advice::WillNeed,
        Advice::DontNeed,
        Advice::NoReuse,
    ] {
        for offset in [0, size.saturating_sub(4096), size, size + 4096] {
            for length in [0, 10, 4096, size, size + 4096] {
                match fd.advise(offset, length, advice).await {
                    Ok(()) => {}
                    Err(err) => {
                        eprintln!("fadvise({}, {}, {:?}) => {}", offset, length, advice, err);
                        process::exit(1);
                    }
                }
            }
        }
    }
}

async fn test_read_directory(dir: &Descriptor) {
    // read-directory: async func() -> tuple<stream<directory-entry>, future<result<_, error-code>>>;
    let (stream, result) = dir.read_directory().await;
    let mut entries = stream.collect().await;
    result.await.unwrap();
    entries.sort_by_key(|e| e.name.clone());
    assert_eq!(
        &entries,
        &[
            DirectoryEntry {
                type_: DescriptorType::RegularFile,
                name: "a.txt".to_string()
            },
            DirectoryEntry {
                type_: DescriptorType::RegularFile,
                name: "b.txt".to_string()
            },
            DirectoryEntry {
                type_: DescriptorType::SymbolicLink,
                name: "parent".to_string()
            }
        ]
    );
}

async fn test_flags_and_type(dir: &Descriptor) {
    // get-flags: async func() -> result<descriptor-flags, error-code>;
    // get-type: async func() -> result<descriptor-type, error-code>;
    let open = |path: &str, oflags: OpenFlags, fdflags: DescriptorFlags| -> _ {
        dir.open_at(PathFlags::empty(), path.to_string(), oflags, fdflags)
    };
    let open_r = |path: &str| -> _ { open(path, OpenFlags::empty(), DescriptorFlags::READ) };
    let creat = |path: &str| -> _ {
        open(
            path,
            OpenFlags::CREATE | OpenFlags::EXCLUSIVE,
            DescriptorFlags::READ | DescriptorFlags::WRITE,
        )
    };
    let rm = |path: &str| dir.unlink_file_at(path.to_string());

    assert_eq!(
        dir.get_flags().await,
        Ok(DescriptorFlags::READ | DescriptorFlags::MUTATE_DIRECTORY)
    );
    assert_eq!(dir.get_type().await, Ok(DescriptorType::Directory));

    let d = open(".", OpenFlags::empty(), DescriptorFlags::empty())
        .await
        .unwrap();
    // No flags opening dir?  Open as read.
    assert_eq!(d.get_flags().await, Ok(DescriptorFlags::READ));
    assert_eq!(d.get_type().await, Ok(DescriptorType::Directory));

    assert_eq!(
        open(".", OpenFlags::empty(), DescriptorFlags::WRITE)
            .await
            .unwrap_err(),
        ErrorCode::IsDirectory
    );

    // FIXME: https://github.com/bytecodealliance/wasmtime/issues/11667
    // let d = open(".", OpenFlags::empty(),
    //              DescriptorFlags::MUTATE_DIRECTORY).await.unwrap();
    // assert_eq!(d.get_flags().await,
    //            Ok(DescriptorFlags::READ | DescriptorFlags::MUTATE_DIRECTORY));
    // assert_eq!(d.get_type().await,
    //            Ok(DescriptorType::Directory));
    //
    // let d = open(".", OpenFlags::empty(),
    //              DescriptorFlags::READ | DescriptorFlags::MUTATE_DIRECTORY).await.unwrap();
    // assert_eq!(d.get_flags().await,
    //            Ok(DescriptorFlags::READ | DescriptorFlags::MUTATE_DIRECTORY));
    // assert_eq!(d.get_type().await,
    //            Ok(DescriptorType::Directory));
    // let d = open(".", OpenFlags::DIRECTORY,
    //              DescriptorFlags::READ | DescriptorFlags::MUTATE_DIRECTORY).await.unwrap();
    // assert_eq!(d.get_flags().await,
    //            Ok(DescriptorFlags::READ | DescriptorFlags::MUTATE_DIRECTORY));
    // assert_eq!(d.get_type().await,
    //            Ok(DescriptorType::Directory));

    let a = open_r("a.txt").await.unwrap();
    assert_eq!(a.get_flags().await, Ok(DescriptorFlags::READ));
    assert_eq!(a.get_type().await, Ok(DescriptorType::RegularFile));
    let c = creat("c.cleanup").await.unwrap();
    assert_eq!(
        c.get_flags().await,
        Ok(DescriptorFlags::READ | DescriptorFlags::WRITE)
    );
    rm("c.cleanup").await.unwrap();

    let c = open(
        "c.cleanup",
        OpenFlags::CREATE | OpenFlags::EXCLUSIVE,
        DescriptorFlags::empty(),
    )
    .await
    .unwrap();
    // CREATE implies WRITE.
    assert_eq!(
        c.get_flags().await,
        Ok(DescriptorFlags::READ | DescriptorFlags::WRITE)
    );
    rm("c.cleanup").await.unwrap();

    let c = open(
        "c.cleanup",
        OpenFlags::CREATE | OpenFlags::EXCLUSIVE,
        DescriptorFlags::READ,
    )
    .await
    .unwrap();
    // CREATE implies WRITE.
    assert_eq!(
        c.get_flags().await,
        Ok(DescriptorFlags::READ | DescriptorFlags::WRITE)
    );
    rm("c.cleanup").await.unwrap();

    let c = open(
        "c.cleanup",
        OpenFlags::CREATE | OpenFlags::EXCLUSIVE,
        DescriptorFlags::WRITE,
    )
    .await
    .unwrap();
    // CREATE implies WRITE, but not READ.
    assert_eq!(c.get_flags().await, Ok(DescriptorFlags::WRITE));
    rm("c.cleanup").await.unwrap();

    // EXCLUSIVE is meaningless without CREATE; flags default to READ.
    let a = open("a.txt", OpenFlags::EXCLUSIVE, DescriptorFlags::empty())
        .await
        .unwrap();
    assert_eq!(a.get_flags().await, Ok(DescriptorFlags::READ));

    // No flags?  Default to READ.
    let a = open("a.txt", OpenFlags::empty(), DescriptorFlags::empty())
        .await
        .unwrap();
    assert_eq!(a.get_flags().await, Ok(DescriptorFlags::READ));

    // WRITE does not imply READ.
    let a = open("a.txt", OpenFlags::empty(), DescriptorFlags::WRITE)
        .await
        .unwrap();
    assert_eq!(a.get_flags().await, Ok(DescriptorFlags::WRITE));
}

async fn test_set_size(dir: &Descriptor) {
    // set-size: async func(size: filesize) -> result<_, error-code>;
    let open = |path: &str, oflags: OpenFlags, fdflags: DescriptorFlags| -> _ {
        dir.open_at(PathFlags::empty(), path.to_string(), oflags, fdflags)
    };
    let open_r = |path: &str| -> _ { open(path, OpenFlags::empty(), DescriptorFlags::READ) };
    let open_w = |path: &str| -> _ {
        open(
            path,
            OpenFlags::empty(),
            DescriptorFlags::READ | DescriptorFlags::WRITE,
        )
    };
    let creat = |path: &str| -> _ {
        open(
            path,
            OpenFlags::CREATE | OpenFlags::EXCLUSIVE,
            DescriptorFlags::READ | DescriptorFlags::WRITE,
        )
    };
    let trunc = |path: &str| -> _ {
        open(
            path,
            OpenFlags::TRUNCATE,
            DescriptorFlags::READ | DescriptorFlags::WRITE,
        )
    };
    let rm = |path: &str| dir.unlink_file_at(path.to_string());

    let c = creat("c.cleanup").await.unwrap();
    assert_eq!(c.stat().await.unwrap().size, 0);
    c.set_size(42).await.unwrap();
    // Setting size is visible immediately.
    assert_eq!(c.stat().await.unwrap().size, 42);

    let c = open_w("c.cleanup").await.unwrap();
    let r = open_r("c.cleanup").await.unwrap();
    assert_eq!(c.stat().await.unwrap().size, 42);
    assert_eq!(r.stat().await.unwrap().size, 42);
    c.set_size(69).await.unwrap();
    assert_eq!(c.stat().await.unwrap().size, 69);
    assert_eq!(r.stat().await.unwrap().size, 69);

    let c = trunc("c.cleanup").await.unwrap();
    assert_eq!(c.stat().await.unwrap().size, 0);
    assert_eq!(r.stat().await.unwrap().size, 0);

    // https://github.com/WebAssembly/wasi-filesystem/issues/190
    match r.set_size(100).await {
        Ok(()) => {
            panic!("set-size succeeded on read-only descriptor");
        }
        Err(ErrorCode::Invalid | ErrorCode::BadDescriptor) => {}
        Err(err) => {
            panic!("unexpected err: {}", err)
        }
    };

    // https://github.com/WebAssembly/wasi-filesystem/issues/190
    match c.set_size(u64::MAX).await {
        Ok(()) => {
            panic!("set-size(-1) succeeded");
        }
        Err(ErrorCode::Invalid | ErrorCode::FileTooLarge) => {}
        Err(err) => {
            panic!("unexpected err: {}", err)
        }
    };

    rm("c.cleanup").await.unwrap();

    // We still have `c` and `r` open, which refer to the file; on POSIX
    // systems, the `c.cleanup` will have been removed from its dir,
    // whereas on Windows that will happen when the last open descriptor
    // (`c` and `r`) is closed.  In any case we can still stat our
    // descriptors, call `set-size` on it, and so on.
    assert_eq!(c.stat().await.unwrap().size, 0);
    c.set_size(42).await.unwrap();
    assert_eq!(c.stat().await.unwrap().size, 42);
    assert_eq!(r.stat().await.unwrap().size, 42);
}

async fn pread(fd: &Descriptor, size: usize, offset: u64) -> Result<Vec<u8>, ErrorCode> {
    let (mut stream, success) = fd.read_via_stream(offset);
    let data = Vec::<u8>::with_capacity(size);
    let (result, data) = stream.read(data).await;
    drop(stream);
    match result {
        StreamResult::Complete(n) => {
            assert_eq!(n, data.len());
            success.await.unwrap();
            Ok(data)
        }
        StreamResult::Dropped => {
            assert_eq!(0, data.len());
            match success.await {
                Ok(()) => Ok(data),
                Err(err) => Err(err),
            }
        }
        StreamResult::Cancelled => {
            panic!("who cancelled the stream?");
        }
    }
}

async fn pwrite(fd: &Descriptor, offset: u64, data: &[u8]) -> Result<usize, ErrorCode> {
    let (mut tx, rx) = wit_stream::new();
    let success = fd.write_via_stream(rx, offset);
    let len = data.len();
    let mut written: usize = 0;
    let (mut result, mut buf) = tx.write(data.to_vec()).await;
    loop {
        match result {
            StreamResult::Complete(n) => {
                assert!(n <= len - written);
                written += n;
                assert_eq!(buf.remaining(), len - written);
                if buf.remaining() != 0 {
                    (result, buf) = tx.write_buf(buf).await;
                } else {
                    break;
                }
            }
            StreamResult::Dropped => {
                panic!("receiver dropped the stream?");
            }
            StreamResult::Cancelled => {
                break;
            }
        }
    }
    assert_eq!(buf.remaining(), len - written);
    drop(tx);
    match success.await {
        Ok(()) => Ok(written),
        Err(err) => Err(err),
    }
}

async fn read_to_eof(fd: &Descriptor, offset: u64) -> Vec<u8> {
    let (stream, success) = fd.read_via_stream(offset);
    let ret = stream.collect().await;
    success.await.unwrap();
    ret
}

async fn test_io(dir: &Descriptor) {
    let open = |path: &str, oflags: OpenFlags, fdflags: DescriptorFlags| -> _ {
        dir.open_at(PathFlags::empty(), path.to_string(), oflags, fdflags)
    };
    let open_r = |path: &str| -> _ { open(path, OpenFlags::empty(), DescriptorFlags::READ) };
    let creat = |path: &str| -> _ {
        open(
            path,
            OpenFlags::CREATE | OpenFlags::EXCLUSIVE,
            DescriptorFlags::READ | DescriptorFlags::WRITE,
        )
    };
    let rm = |path: &str| dir.unlink_file_at(path.to_string());

    let a = open_r("a.txt").await.unwrap();

    pread(&a, 0, 0).await.unwrap();
    pread(&a, 0, 1).await.unwrap();
    pread(&a, 0, 6).await.unwrap();
    pread(&a, 0, 7).await.unwrap();
    pread(&a, 0, 17).await.unwrap();

    assert_eq!(&pread(&a, 1, 0).await.unwrap(), b"t");
    assert_eq!(&pread(&a, 1, 1).await.unwrap(), b"e");
    assert_eq!(&pread(&a, 1, 6).await.unwrap(), b"\n");
    assert_eq!(&pread(&a, 1, 7).await.unwrap(), b"");
    assert_eq!(&pread(&a, 1, 17).await.unwrap(), b"");

    assert_eq!(&read_to_eof(&a, 0).await, b"test-a\n");
    assert_eq!(&read_to_eof(&a, 1).await, b"est-a\n");
    assert_eq!(&read_to_eof(&a, 6).await, b"\n");
    assert_eq!(&read_to_eof(&a, 7).await, b"");
    assert_eq!(&read_to_eof(&a, 17).await, b"");

    assert_eq!(pread(&a, 1, u64::MAX).await, Err(ErrorCode::Invalid));

    let c = creat("c.cleanup").await.unwrap();
    assert_eq!(&read_to_eof(&c, 0).await, b"");
    assert_eq!(pwrite(&c, 0, b"hello!").await, Ok(b"hello!".len()));
    assert_eq!(&read_to_eof(&c, 0).await, b"hello!");
    rm("c.cleanup").await.unwrap();

    // append-via-stream: async func(data: stream<u8>) -> result<_, error-code>;
    // sync-data: async func() -> result<_, error-code>;
    // sync: async func() -> result<_, error-code>;
}

async fn test_filesystem() {
    match &wasi::filesystem::preopens::get_directories()[..] {
        [(dir, dirname)] if dirname == "fs-tests.dir" => {
            check_test_harness(dir).await;

            test_mkdir_rmdir(dir).await;
            test_stat(dir).await;
            test_hard_links(dir).await;
            test_rename(dir).await;
            test_symbolic_links(dir).await;
            test_is_same_object(dir).await;
            test_metadata_hash(dir).await;
            test_open_errors(dir).await;
            test_unlink_errors(dir).await;
            test_advise(dir).await;
            test_read_directory(dir).await;
            test_flags_and_type(dir).await;
            test_set_size(dir).await;
            test_io(dir).await;
        }
        [..] => {
            eprintln!("usage: run with one open dir named 'fs-tests.dir'");
            process::exit(1)
        }
    }
}

struct Component;
export!(Component);
impl exports::wasi::cli::run::Guest for Component {
    async fn run() -> Result<(), ()> {
        test_filesystem().await;
        Ok(())
    }
}

fn main() {
    unreachable!("main is a stub");
}
