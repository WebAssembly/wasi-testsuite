use std::{env, process};
use wasi_tests::{assert_errno, create_file, create_tmp_dir, open_scratch_directory};

unsafe fn test_path_open_create_existing(dir_fd: wasi::Fd) {
    create_file(dir_fd, "file");
    assert_errno!(
        wasi::path_open(
            dir_fd,
            0,
            "file",
            wasi::OFLAGS_CREAT | wasi::OFLAGS_EXCL,
            0,
            0,
            0,
        )
        .expect_err("trying to create a file that already exists"),
        wasi::ERRNO_EXIST
    );
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

    const DIR_NAME: &str = "path_open_create_existing_dir.cleanup";
    let dir_fd;
    unsafe {
        dir_fd = create_tmp_dir(base_dir_fd, DIR_NAME);
    }

    // Run the tests.
    unsafe { test_path_open_create_existing(dir_fd) }

    unsafe { wasi::path_remove_directory(base_dir_fd, DIR_NAME).expect("failed to remove dir") }
}
