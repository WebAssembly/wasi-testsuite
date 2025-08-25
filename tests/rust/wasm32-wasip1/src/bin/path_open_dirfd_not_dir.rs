use std::{env, process};
use wasi_tests::{assert_errno, create_tmp_dir, open_scratch_directory};

unsafe fn test_dirfd_not_dir(dir_fd: wasi::Fd) {
    // Open a file.
    let file_fd =
        wasi::path_open(dir_fd, 0, "file", wasi::OFLAGS_CREAT, 0, 0, 0).expect("opening a file");
    // Now try to open a file underneath it as if it were a directory.
    assert_errno!(
        wasi::path_open(file_fd, 0, "foo", wasi::OFLAGS_CREAT, 0, 0, 0)
            .expect_err("non-directory base fd should get ERRNO_NOTDIR"),
        wasi::ERRNO_NOTDIR,
        wasi::ERRNO_NOTCAPABLE
    );
    wasi::fd_close(file_fd).expect("closing a file");
    wasi::path_unlink_file(dir_fd, "file").expect("removing a file");
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

    const DIR_NAME: &str = "path_open_dirfd_not_dir_dir.cleanup";
    let dir_fd;
    unsafe {
        dir_fd = create_tmp_dir(base_dir_fd, DIR_NAME);
    }

    // Run the tests.
    unsafe { test_dirfd_not_dir(dir_fd) }

    unsafe { wasi::path_remove_directory(base_dir_fd, DIR_NAME).expect("failed to remove dir") }
}
