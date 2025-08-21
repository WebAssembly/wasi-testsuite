use std::{env, process};
use wasi_tests::open_scratch_directory;

unsafe fn test_fstflags_validate(dir_fd: wasi::Fd) {
    const FILE_NAME: &str = "fstflags_validate.cleanup";

    let file_fd = wasi::path_open(
        dir_fd,
        0,
        FILE_NAME,
        wasi::OFLAGS_CREAT,
        wasi::RIGHTS_FD_READ | wasi::RIGHTS_FD_FILESTAT_SET_TIMES,
        0,
        0,
    )
    .expect("failed to create file");

    let result = wasi::fd_filestat_set_times(
        file_fd,
        100,
        200,
        wasi::FSTFLAGS_MTIM | wasi::FSTFLAGS_MTIM_NOW,
    );
    assert!(matches!(result, Err(wasi::ERRNO_INVAL)));

    let result = wasi::fd_filestat_set_times(
        file_fd,
        100,
        200,
        wasi::FSTFLAGS_ATIM | wasi::FSTFLAGS_ATIM_NOW,
    );
    assert!(matches!(result, Err(wasi::ERRNO_INVAL)));

    wasi::fd_close(file_fd).expect("failed to close fd");
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
    let dir_fd = match open_scratch_directory(&arg) {
        Ok(dir_fd) => dir_fd,
        Err(err) => {
            eprintln!("{}", err);
            process::exit(1)
        }
    };

    // Run the tests.
    unsafe { test_fstflags_validate(dir_fd) }
}
