use std::{env, process};
use wasi_tests::root_directory;
use wasip1 as wasi;

unsafe fn try_path_open(dir_fd: wasi::Fd) {
    let _fd =
        wasi::path_open(dir_fd, 0, ".", 0, 0, 0, wasi::FDFLAGS_NONBLOCK).expect("opening the dir");
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
    unsafe { try_path_open(dir_fd) }
}
