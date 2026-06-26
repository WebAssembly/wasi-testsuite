use std::{env, process};
use wasi_tests::{TESTCONFIG, assert_errno, create_tmp_dir, root_directory};
use wasip1 as wasi;

unsafe fn test_symlink_loop(dir_fd: wasi::Fd) {
    if TESTCONFIG.support_dangling_filesystem()
        && wasi::path_symlink("symlink", dir_fd, "symlink").is_ok()
    {
        // Try to open it.
        assert_errno!(
            wasi::path_open(dir_fd, 0, "symlink", 0, 0, 0, 0)
                .expect_err("opening a self-referencing symlink"),
            wasi::ERRNO_LOOP
        );

        // Clean up.
        wasi::path_unlink_file(dir_fd, "symlink").expect("removing a file");
    }
}

fn main() {
    let base_dir_fd = match root_directory() {
        Ok(dir_fd) => dir_fd,
        Err(err) => {
            eprintln!("{}", err);
            process::exit(1)
        }
    };

    const DIR_NAME: &str = "symlink_loop_dir.cleanup";
    let dir_fd;
    unsafe {
        dir_fd = create_tmp_dir(base_dir_fd, DIR_NAME);
    }

    // Run the tests.
    unsafe { test_symlink_loop(dir_fd) }

    unsafe {
        wasi::fd_close(dir_fd).unwrap();
    }
    unsafe { wasi::path_remove_directory(base_dir_fd, DIR_NAME).expect("failed to remove dir") }
}
