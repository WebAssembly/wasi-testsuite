use std::{env, process};

use wasi_tests::{create_tmp_dir, open_scratch_directory, STDERR_FD, STDIN_FD, STDOUT_FD};

const TEST_FILENAME: &'static str = "file.cleanup";

unsafe fn test_stdio(dir_fd: wasi::Fd) {
    for stdio_from_fd in &[STDIN_FD, STDOUT_FD, STDERR_FD] {
        let stdio_to_fd = wasi::path_open(dir_fd, 0, TEST_FILENAME, wasi::OFLAGS_CREAT, 0, 0, 0)
            .expect("open file");

        wasi::fd_renumber(*stdio_from_fd, stdio_to_fd).expect("renumbering stdio");

        wasi::fd_fdstat_get(stdio_to_fd).expect("fd_fdstat_get failed");
        wasi::fd_fdstat_get(*stdio_from_fd).expect_err("stdio_from_fd is not closed");

        // Cleanup
        wasi::path_unlink_file(dir_fd, TEST_FILENAME).expect("failed to remove file");
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

    let base_dir_fd = match open_scratch_directory(&arg) {
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

    unsafe { wasi::path_remove_directory(base_dir_fd, DIR_NAME).expect("failed to remove dir") }
}
