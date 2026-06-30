use std::{env, process};
use wasi_tests::{TESTCONFIG, assert_errno, root_directory};
use wasip1 as wasi;

unsafe fn test_dangling_symlink(dir_fd: wasi::Fd) {
    if TESTCONFIG.support_dangling_filesystem() {
        const SYMLINK_NAME: &str = "dangling_symlink_symlink.cleanup";
        // First create a dangling symlink.
        if wasi::path_symlink("target", dir_fd, SYMLINK_NAME).is_err() {
            return;
        }

        // Try to open it as a directory with O_NOFOLLOW.
        assert_errno!(
            wasi::path_open(dir_fd, 0, SYMLINK_NAME, wasi::OFLAGS_DIRECTORY, 0, 0, 0)
                .expect_err("opening a dangling symlink as a directory"),
            wasi::ERRNO_NOTDIR,
            wasi::ERRNO_LOOP
        );

        // Try to open it as a file with O_NOFOLLOW.
        assert_errno!(
            wasi::path_open(dir_fd, 0, SYMLINK_NAME, 0, 0, 0, 0)
                .expect_err("opening a dangling symlink as a file"),
            wasi::ERRNO_LOOP
        );

        // Clean up.
        wasi::path_unlink_file(dir_fd, SYMLINK_NAME).expect("failed to remove file");
    }
}

fn main() {
    let dir_fd = match root_directory() {
        Ok(dir_fd) => dir_fd,
        Err(err) => {
            eprintln!("{}", err);
            process::exit(1)
        }
    };

    // Run the tests.
    unsafe { test_dangling_symlink(dir_fd) }
}
