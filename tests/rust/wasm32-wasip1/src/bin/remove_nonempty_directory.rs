use std::{env, process};
use wasi_tests::{assert_errno, create_tmp_dir, root_directory};
use wasip1 as wasi;

unsafe fn test_remove_nonempty_directory(dir_fd: wasi::Fd) {
    // Create a directory in the scratch directory.
    wasi::path_create_directory(dir_fd, "dir").expect("creating a directory");

    // Create a directory in the directory we just created.
    wasi::path_create_directory(dir_fd, "dir/nested").expect("creating a subdirectory");

    // Test that attempting to unlink the first directory returns the expected error code.
    assert_errno!(
        wasi::path_remove_directory(dir_fd, "dir")
            .expect_err("remove_directory on a directory should return ENOTEMPTY"),
        wasi::ERRNO_NOTEMPTY
    );

    // Removing the directories.
    wasi::path_remove_directory(dir_fd, "dir/nested")
        .expect("remove_directory on a nested directory should succeed");
    wasi::path_remove_directory(dir_fd, "dir").expect("removing a directory");
}

fn main() {
    let base_dir_fd = match root_directory() {
        Ok(dir_fd) => dir_fd,
        Err(err) => {
            eprintln!("{}", err);
            process::exit(1)
        }
    };

    const DIR_NAME: &str = "remove_nonempty_directory_dir.cleanup";
    let dir_fd;
    unsafe {
        dir_fd = create_tmp_dir(base_dir_fd, DIR_NAME);
    }

    // Run the tests.
    unsafe { test_remove_nonempty_directory(dir_fd) }

    unsafe {
        wasi::fd_close(dir_fd).unwrap();
    }
    unsafe { wasi::path_remove_directory(base_dir_fd, DIR_NAME).expect("failed to remove dir") }
}
