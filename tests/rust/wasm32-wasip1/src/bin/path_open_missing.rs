use std::{env, process};
use wasi_tests::{assert_errno, create_tmp_dir, open_scratch_directory};

unsafe fn test_path_open_missing(dir_fd: wasi::Fd) {
    assert_errno!(
        wasi::path_open(
            dir_fd, 0, "file", 0, // not passing O_CREAT here
            0, 0, 0,
        )
        .expect_err("trying to open a file that doesn't exist"),
        wasi::ERRNO_NOENT
    );
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

    // Open scratch directory
    let base_dir_fd = match open_scratch_directory(&arg) {
        Ok(dir_fd) => dir_fd,
        Err(err) => {
            eprintln!("{}", err);
            process::exit(1)
        }
    };

    const DIR_NAME: &str = "path_open_missing_dir.cleanup";
    let dir_fd;
    unsafe {
        dir_fd = create_tmp_dir(base_dir_fd, DIR_NAME);
    }

    // Run the tests.
    unsafe { test_path_open_missing(dir_fd) }

    unsafe { wasi::path_remove_directory(base_dir_fd, DIR_NAME).expect("failed to remove dir") }
}
