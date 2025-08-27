use std::{env, process};

unsafe fn find_first_preopened_fd(path: &str) -> Result<wasi::Fd, String> {
    let max_fd = (1 << 31) - 1;

    for i in 3..=max_fd {
        match wasi::fd_prestat_get(i) {
            Ok(prestat) => {
                if prestat.tag != wasi::PREOPENTYPE_DIR.raw() {
                    continue;
                }
                let mut dst = Vec::with_capacity(prestat.u.dir.pr_name_len);

                if wasi::fd_prestat_dir_name(i, dst.as_mut_ptr(), dst.capacity()).is_err() {
                    continue;
                }
                dst.set_len(prestat.u.dir.pr_name_len);

                if dst == path.as_bytes() {
                    return Ok(i);
                }
            }
            Err(_) => continue,
        };
    }

    Err(format!("Failed to find a preopened directory"))
}

unsafe fn path_open_preopen(preopened_fd: wasi::Fd) {
    let prestat = wasi::fd_prestat_get(preopened_fd).expect("fd is a preopen");
    assert_eq!(
        prestat.tag,
        wasi::PREOPENTYPE_DIR.raw(),
        "prestat is a directory"
    );
    let mut dst = Vec::with_capacity(prestat.u.dir.pr_name_len);
    wasi::fd_prestat_dir_name(preopened_fd, dst.as_mut_ptr(), dst.capacity())
        .expect("get preopen dir name");
    dst.set_len(prestat.u.dir.pr_name_len);

    let fdstat = wasi::fd_fdstat_get(preopened_fd).expect("get fdstat");

    println!(
        "preopen dir: {:?} base {:?} inheriting {:?}",
        String::from_utf8_lossy(&dst),
        fdstat.fs_rights_base,
        fdstat.fs_rights_inheriting
    );
    for (right, name) in directory_base_rights() {
        assert!(
            (fdstat.fs_rights_base & right) == right,
            "fs_rights_base does not have required right `{name}`"
        );
    }
    for (right, name) in directory_inheriting_rights() {
        assert!(
            (fdstat.fs_rights_inheriting & right) == right,
            "fs_rights_inheriting does not have required right `{name}`"
        );
    }

    // Open with same rights it has now:
    let _ = wasi::path_open(
        preopened_fd,
        0,
        ".",
        0,
        fdstat.fs_rights_base,
        fdstat.fs_rights_inheriting,
        0,
    )
    .expect("open with same rights");

    // Open with an empty set of rights:
    let _ = wasi::path_open(preopened_fd, 0, ".", 0, 0, 0, 0).expect("open with empty rights");

    // Open OFLAGS_DIRECTORY with an empty set of rights:
    let _ = wasi::path_open(preopened_fd, 0, ".", wasi::OFLAGS_DIRECTORY, 0, 0, 0)
        .expect("open with O_DIRECTORY empty rights");

    // Open OFLAGS_DIRECTORY with just the read right:
    let _ = wasi::path_open(
        preopened_fd,
        0,
        ".",
        wasi::OFLAGS_DIRECTORY,
        wasi::RIGHTS_FD_READ,
        0,
        0,
    )
    .expect("open with O_DIRECTORY and read right");

    if !wasi_tests::TESTCONFIG.errno_expect_windows() {
        // Open OFLAGS_DIRECTORY and read/write rights should fail with isdir:
        let err = wasi::path_open(
            preopened_fd,
            0,
            ".",
            wasi::OFLAGS_DIRECTORY,
            wasi::RIGHTS_FD_READ | wasi::RIGHTS_FD_WRITE,
            0,
            0,
        )
        .err()
        .expect("open with O_DIRECTORY and read/write should fail");
        assert_eq!(
            err,
            wasi::ERRNO_ISDIR,
            "opening directory read/write should fail with ISDIR"
        );
    } else {
        // Open OFLAGS_DIRECTORY and read/write rights will succeed, only on windows:
        let _ = wasi::path_open(
            preopened_fd,
            0,
            ".",
            wasi::OFLAGS_DIRECTORY,
            wasi::RIGHTS_FD_READ | wasi::RIGHTS_FD_WRITE,
            0,
            0,
        )
        .expect("open with O_DIRECTORY and read/write should succeed on windows");
    }
}

fn main() {
    let mut args = env::args();
    let prog = args.next().unwrap();

    let arg = if let Some(arg) = args.next() {
        arg
    } else {
        eprintln!("usage: {} <scratch directory>", prog);
        process::exit(1);
    };

    let preopened_fd = unsafe { find_first_preopened_fd(arg.as_str()).unwrap() };

    // Run the tests.
    unsafe { path_open_preopen(preopened_fd) }
}

// Hard-code the set of rights expected for a preopened directory. This is
// more brittle than we wanted to test for, but various userland
// implementations expect (at least) this set of rights to be present on all
// directories:

fn directory_base_rights() -> Vec<(wasi::Rights, &'static str)> {
    vec![
        (wasi::RIGHTS_PATH_CREATE_DIRECTORY, "PATH_CREATE_DIRECTORY"),
        (wasi::RIGHTS_PATH_CREATE_FILE, "PATH_CREATE_FILE"),
        (wasi::RIGHTS_PATH_LINK_SOURCE, "PATH_LINK_SOURCE"),
        (wasi::RIGHTS_PATH_LINK_TARGET, "PATH_LINK_TARGET"),
        (wasi::RIGHTS_PATH_OPEN, "PATH_OPEN"),
        (wasi::RIGHTS_FD_READDIR, "FD_READDIR"),
        (wasi::RIGHTS_PATH_READLINK, "PATH_READLINK"),
        (wasi::RIGHTS_PATH_RENAME_SOURCE, "PATH_RENAME_SOURCE"),
        (wasi::RIGHTS_PATH_RENAME_TARGET, "PATH_RENAME_TARGET"),
        (wasi::RIGHTS_PATH_SYMLINK, "PATH_SYMLINK"),
        (wasi::RIGHTS_PATH_REMOVE_DIRECTORY, "PATH_REMOVE_DIRECTORY"),
        (wasi::RIGHTS_PATH_UNLINK_FILE, "PATH_UNLINK_FILE"),
        (wasi::RIGHTS_PATH_FILESTAT_GET, "PATH_FILESTAT_GET"),
        (
            wasi::RIGHTS_PATH_FILESTAT_SET_TIMES,
            "PATH_FILESTAT_SET_TIMES",
        ),
        (wasi::RIGHTS_FD_FILESTAT_GET, "FD_FILESTAT_GET"),
        (wasi::RIGHTS_FD_FILESTAT_SET_TIMES, "FD_FILESTAT_SET_TIMES"),
    ]
}

pub(crate) fn directory_inheriting_rights() -> Vec<(wasi::Rights, &'static str)> {
    let mut rights = directory_base_rights();
    rights.extend_from_slice(&[
        (wasi::RIGHTS_FD_DATASYNC, "FD_DATASYNC"),
        (wasi::RIGHTS_FD_READ, "FD_READ"),
        (wasi::RIGHTS_FD_SEEK, "FD_SEEK"),
        (wasi::RIGHTS_FD_FDSTAT_SET_FLAGS, "FD_FDSTAT_SET_FLAGS"),
        (wasi::RIGHTS_FD_SYNC, "FD_SYNC"),
        (wasi::RIGHTS_FD_TELL, "FD_TELL"),
        (wasi::RIGHTS_FD_WRITE, "FD_WRITE"),
        (wasi::RIGHTS_FD_ADVISE, "FD_ADVISE"),
        (wasi::RIGHTS_FD_ALLOCATE, "FD_ALLOCATE"),
        (wasi::RIGHTS_FD_FILESTAT_GET, "FD_FILESTAT_GET"),
        (wasi::RIGHTS_FD_FILESTAT_SET_SIZE, "FD_FILESTAT_SET_SIZE"),
        (wasi::RIGHTS_FD_FILESTAT_SET_TIMES, "FD_FILESTAT_SET_TIMES"),
        (wasi::RIGHTS_POLL_FD_READWRITE, "POLL_FD_READWRITE"),
    ]);
    rights
}
