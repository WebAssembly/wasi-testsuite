use std::{env, process};
use wasi_tests::{assert_errno, create_file, root_directory};

const TEST_FILENAME: &'static str = "file.cleanup";
const TEST_DIRNAME: &'static str = "dir.cleanup";

unsafe fn test_remove_directory_trailing_slashes(dir_fd: wasi::Fd) {
    // Create a directory in the scratch directory.
    wasi::path_create_directory(dir_fd, TEST_DIRNAME).expect("creating a directory");

    // Test that removing it succeeds.
    wasi::path_remove_directory(dir_fd, TEST_DIRNAME)
        .expect("remove_directory on a directory should succeed");

    wasi::path_create_directory(dir_fd, TEST_DIRNAME).expect("creating a directory");

    // Test that removing it with a trailing slash succeeds.
    match wasi::path_remove_directory(dir_fd, &format!("{}/", TEST_DIRNAME)) {
        Ok(()) => {}
        Err(e) => {
            assert_errno!(e, wasi::ERRNO_ACCES, wasi::ERRNO_INVAL);
            wasi::path_remove_directory(dir_fd, TEST_DIRNAME).unwrap();
        }
    }

    // Create a temporary file.
    create_file(dir_fd, TEST_FILENAME);

    // Test that removing it with no trailing slash fails.
    assert_errno!(
        wasi::path_remove_directory(dir_fd, TEST_FILENAME)
            .expect_err("remove_directory without a trailing slash on a file should fail"),
        wasi::ERRNO_NOTDIR
    );

    // Test that removing it with a trailing slash fails.
    assert_errno!(
        wasi::path_remove_directory(dir_fd, &format!("{}/", TEST_FILENAME))
            .expect_err("remove_directory with a trailing slash on a file should fail"),
        unix => wasi::ERRNO_NOTDIR,
        windows => wasi::ERRNO_NOENT
    );

    wasi::path_unlink_file(dir_fd, TEST_FILENAME).expect("removing a file");
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
    unsafe { test_remove_directory_trailing_slashes(dir_fd) }
}
