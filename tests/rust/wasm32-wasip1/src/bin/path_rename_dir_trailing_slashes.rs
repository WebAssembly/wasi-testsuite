use std::{env, process};
use wasi_tests::{create_tmp_dir, root_directory};
use wasip1 as wasi;

unsafe fn test_path_rename_trailing_slashes(dir_fd: wasi::Fd) {
    // Test renaming a directory with a trailing slash in the name.
    wasi::path_create_directory(dir_fd, "source").expect("creating a directory");
    wasi::path_rename(dir_fd, "source/", dir_fd, "target")
        .expect("renaming a directory with a trailing slash in the source name");
    wasi::path_rename(dir_fd, "target", dir_fd, "source/")
        .expect("renaming a directory with a trailing slash in the destination name");
    wasi::path_rename(dir_fd, "source/", dir_fd, "target/")
        .expect("renaming a directory with a trailing slash in the source and destination names");
    wasi::path_rename(dir_fd, "target", dir_fd, "source")
        .expect("renaming a directory with no trailing slashes at all should work");
    wasi::path_remove_directory(dir_fd, "source").expect("removing the directory");
}

fn main() {
    let base_dir_fd = match root_directory() {
        Ok(dir_fd) => dir_fd,
        Err(err) => {
            eprintln!("{}", err);
            process::exit(1)
        }
    };

    const DIR_NAME: &str = "path_rename_dir_trailing_slashes_dir.cleanup";
    let dir_fd;
    unsafe {
        dir_fd = create_tmp_dir(base_dir_fd, DIR_NAME);
    }

    // Run the tests.
    unsafe { test_path_rename_trailing_slashes(dir_fd) }

    unsafe {
        wasi::fd_close(dir_fd).unwrap();
    }
    unsafe { wasi::path_remove_directory(base_dir_fd, DIR_NAME).expect("failed to remove dir") }
}
