use std::{env, process};
use wasi_tests::{assert_errno, create_file, create_tmp_dir, open_scratch_directory};

unsafe fn test_unlink_file_trailing_slashes(dir_fd: wasi::Fd) {
    // Create a directory in the scratch directory.
    wasi::path_create_directory(dir_fd, "dir").expect("creating a directory");

    // Test that unlinking it fails.
    assert_errno!(
        wasi::path_unlink_file(dir_fd, "dir")
            .expect_err("unlink_file on a directory should fail"),
        macos => wasi::ERRNO_PERM,
        unix => wasi::ERRNO_ISDIR,
        windows => wasi::ERRNO_ACCES
    );

    // Test that unlinking it with a trailing flash fails.
    assert_errno!(
        wasi::path_unlink_file(dir_fd, "dir/")
            .expect_err("unlink_file on a directory should fail"),
        macos => wasi::ERRNO_PERM,
        unix => wasi::ERRNO_ISDIR,
        windows => wasi::ERRNO_ACCES
    );

    // Clean up.
    wasi::path_remove_directory(dir_fd, "dir").expect("removing a directory");

    // Create a temporary file.
    create_file(dir_fd, "file");

    // Test that unlinking it with a trailing flash fails.
    assert_errno!(
        wasi::path_unlink_file(dir_fd, "file/")
            .expect_err("unlink_file with a trailing slash should fail"),
        unix => wasi::ERRNO_NOTDIR,
        windows => wasi::ERRNO_NOENT
    );

    // Test that unlinking it with no trailing flash succeeds.
    wasi::path_unlink_file(dir_fd, "file")
        .expect("unlink_file with no trailing slash should succeed");
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

    const DIR_NAME: &str = "unlink_file_trailing_slashes_dir.cleanup";
    let dir_fd;
    unsafe {
        dir_fd = create_tmp_dir(base_dir_fd, DIR_NAME);
    }

    // Run the tests.
    unsafe { test_unlink_file_trailing_slashes(dir_fd) }

    unsafe { wasi::path_remove_directory(base_dir_fd, DIR_NAME).expect("failed to remove dir") }
}
