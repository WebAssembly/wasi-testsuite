use std::{env, process};
use wasi::path_create_directory;
use wasi_tests::{assert_errno, create_file, root_directory};
use wasip1 as wasi;

unsafe fn test_interesting_paths(dir_fd: wasi::Fd) {
    // Create a directory in the scratch directory.
    wasi::path_create_directory(dir_fd, "dir").expect("creating dir");

    // Create a directory in the directory we just created.
    wasi::path_create_directory(dir_fd, "dir/nested").expect("creating a nested dir");

    // Create a file in the nested directory.
    create_file(dir_fd, "dir/nested/file");

    // Now open it with an absolute path.
    assert_errno!(
        wasi::path_open(dir_fd, 0, "/dir/nested/file", 0, 0, 0, 0)
            .expect_err("opening a file with an absolute path"),
        wasi::ERRNO_PERM,
        wasi::ERRNO_NOTCAPABLE
    );

    // Now open it with a path containing "..".
    let mut file_fd = wasi::path_open(
        dir_fd,
        0,
        "dir/.//nested/../../dir/nested/../nested///./file",
        0,
        0,
        0,
        0,
    )
    .expect("opening a file with \"..\" in the path");
    assert!(
        file_fd > libc::STDERR_FILENO as wasi::Fd,
        "file descriptor range check",
    );
    wasi::fd_close(file_fd).expect("closing a file");

    // Now open it with a trailing NUL.
    assert_errno!(
        wasi::path_open(dir_fd, 0, "dir/nested/file\0", 0, 0, 0, 0)
            .expect_err("opening a file with a trailing NUL"),
        wasi::ERRNO_INVAL,
        wasi::ERRNO_ILSEQ,
        wasi::ERRNO_NOENT
    );

    // Now open it with a trailing slash.
    assert_errno!(
        wasi::path_open(dir_fd, 0, "dir/nested/file/", 0, 0, 0, 0)
            .expect_err("opening a file with a trailing slash should fail"),
        wasi::ERRNO_NOTDIR,
        wasi::ERRNO_NOENT
    );

    // Now open it with trailing slashes.
    assert_errno!(
        wasi::path_open(dir_fd, 0, "dir/nested/file///", 0, 0, 0, 0)
            .expect_err("opening a file with trailing slashes should fail"),
        wasi::ERRNO_NOTDIR,
        wasi::ERRNO_NOENT
    );

    // Now open the directory with a trailing slash.
    file_fd = wasi::path_open(dir_fd, 0, "dir/nested/", 0, 0, 0, 0)
        .expect("opening a directory with a trailing slash");
    assert!(
        file_fd > libc::STDERR_FILENO as wasi::Fd,
        "file descriptor range check",
    );
    wasi::fd_close(file_fd).expect("closing a file");

    // Now open the directory with trailing slashes.
    file_fd = wasi::path_open(dir_fd, 0, "dir/nested///", 0, 0, 0, 0)
        .expect("opening a directory with trailing slashes");
    assert!(
        file_fd > libc::STDERR_FILENO as wasi::Fd,
        "file descriptor range check",
    );
    wasi::fd_close(file_fd).expect("closing a file");

    // Now open it with a path containing too many ".."s.
    let bad_path = "dir/nested/../../../dir/nested/file";
    assert_errno!(
        wasi::path_open(dir_fd, 0, bad_path, 0, 0, 0, 0)
            .expect_err("opening a file with too many \"..\"s in the path should fail"),
        wasi::ERRNO_PERM,
        wasi::ERRNO_NOTCAPABLE
    );
    wasi::path_unlink_file(dir_fd, "dir/nested/file")
        .expect("unlink_file on a symlink should succeed");
    wasi::path_remove_directory(dir_fd, "dir/nested")
        .expect("remove_directory on a directory should succeed");
    wasi::path_remove_directory(dir_fd, "dir")
        .expect("remove_directory on a directory should succeed");
}

unsafe fn create_tmp_dir(dir_fd: wasi::Fd, name: &str) -> wasi::Fd {
    path_create_directory(dir_fd, name).expect("failed to create dir");
    wasi::path_open(
        dir_fd,
        0,
        name,
        wasi::OFLAGS_DIRECTORY,
        wasi::RIGHTS_FD_FILESTAT_GET
            | wasi::RIGHTS_FD_READDIR
            | wasi::RIGHTS_PATH_CREATE_FILE
            | wasi::RIGHTS_PATH_CREATE_DIRECTORY
            | wasi::RIGHTS_PATH_REMOVE_DIRECTORY
            | wasi::RIGHTS_PATH_OPEN
            | wasi::RIGHTS_PATH_UNLINK_FILE,
        wasi::RIGHTS_FD_READ
            | wasi::RIGHTS_FD_WRITE
            | wasi::RIGHTS_FD_READDIR
            | wasi::RIGHTS_FD_FILESTAT_GET
            | wasi::RIGHTS_FD_SEEK,
        0,
    )
    .expect("failed to open dir")
}

fn main() {
    let base_dir_fd = match root_directory() {
        Ok(dir_fd) => dir_fd,
        Err(err) => {
            eprintln!("{}", err);
            process::exit(1)
        }
    };

    const DIR_NAME: &str = "interesting_paths_dir.cleanup";
    let dir_fd;
    unsafe {
        dir_fd = create_tmp_dir(base_dir_fd, DIR_NAME);
    }

    // Run the tests.
    unsafe { test_interesting_paths(dir_fd) }

    unsafe {
        wasi::fd_close(dir_fd).unwrap();
    }
    unsafe { wasi::path_remove_directory(base_dir_fd, DIR_NAME).expect("failed to remove dir") }
}
