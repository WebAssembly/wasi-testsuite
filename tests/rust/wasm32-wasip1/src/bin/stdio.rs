use std::{env, process};
use wasip1 as wasi;

use wasi_tests::{STDERR_FD, STDIN_FD, STDOUT_FD, create_tmp_dir, root_directory};

const TEST_FILENAME: &'static str = "file.cleanup";

unsafe fn test_stdio(dir_fd: wasi::Fd) {
    for stdio_from_fd in &[STDIN_FD, STDOUT_FD, STDERR_FD] {
        let stdio_to_fd = wasi::path_open(dir_fd, 0, TEST_FILENAME, wasi::OFLAGS_CREAT, 0, 0, 0)
            .expect("open file");
        eprintln!("{stdio_from_fd} => {stdio_to_fd}");

        wasi::fd_renumber(*stdio_from_fd, stdio_to_fd).expect("renumbering stdio");

        wasi::fd_fdstat_get(stdio_to_fd).expect("fd_fdstat_get failed");
        wasi::fd_fdstat_get(*stdio_from_fd).expect_err("stdio_from_fd is not closed");

        // Cleanup
        wasi::path_unlink_file(dir_fd, TEST_FILENAME).expect("failed to remove file");
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

    const DIR_NAME: &str = "stdio_dir.cleanup";
    let dir_fd;
    unsafe {
        dir_fd = create_tmp_dir(base_dir_fd, DIR_NAME);
    }
    // Run the tests.
    unsafe { test_stdio(dir_fd) }

    unsafe {
        wasi::fd_close(dir_fd).unwrap();
    }
    unsafe { wasi::path_remove_directory(base_dir_fd, DIR_NAME).expect("failed to remove dir") }
}
