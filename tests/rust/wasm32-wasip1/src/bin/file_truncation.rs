use std::{env, process};
use wasi_tests::{create_tmp_dir, root_directory};
use wasip1 as wasi;

unsafe fn test_file_truncation(dir_fd: wasi::Fd) {
    const FILENAME: &str = "test.txt";

    // Open a file for writing
    let file_fd = wasi::path_open(
        dir_fd,
        0,
        FILENAME,
        wasi::OFLAGS_CREAT,
        wasi::RIGHTS_FD_WRITE,
        0,
        0,
    )
    .expect("creating a file for writing");

    // Write to the file
    let content = b"this content will be truncated!";
    let nwritten = wasi::fd_write(
        file_fd,
        &[wasi::Ciovec {
            buf: content.as_ptr() as *const _,
            buf_len: content.len(),
        }],
    )
    .expect("writing file content");
    assert_eq!(nwritten, content.len(), "nwritten bytes check");

    wasi::fd_close(file_fd).expect("closing the file");

    // Open the file for truncation
    let file_fd = wasi::path_open(
        dir_fd,
        0,
        FILENAME,
        wasi::OFLAGS_CREAT | wasi::OFLAGS_TRUNC,
        wasi::RIGHTS_FD_WRITE | wasi::RIGHTS_FD_READ,
        0,
        0,
    )
    .expect("creating a truncated file for reading");

    // Read the file's contents
    let buffer = &mut [0u8; 100];
    let nread = wasi::fd_read(
        file_fd,
        &[wasi::Iovec {
            buf: buffer.as_mut_ptr(),
            buf_len: buffer.len(),
        }],
    )
    .expect("reading file content");

    // The file should be empty due to truncation
    assert_eq!(nread, 0, "expected an empty file after truncation");

    wasi::fd_close(file_fd).expect("closing the file");

    wasi::path_unlink_file(dir_fd, FILENAME).expect("removing FILENAME");
}

fn main() {
    let base_dir_fd = match root_directory() {
        Ok(dir_fd) => dir_fd,
        Err(err) => {
            eprintln!("{}", err);
            process::exit(1)
        }
    };

    const DIR_NAME: &str = "file_truncation_dir.cleanup";
    let dir_fd;
    unsafe {
        dir_fd = create_tmp_dir(base_dir_fd, DIR_NAME);
    }

    // Run the tests.
    unsafe { test_file_truncation(dir_fd) }

    unsafe {
        wasi::fd_close(dir_fd).unwrap();
    }
    unsafe { wasi::path_remove_directory(base_dir_fd, DIR_NAME).expect("failed to remove dir") }
}
