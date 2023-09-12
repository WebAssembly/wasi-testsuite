use std::{env, process};
use wasi_tests::{
    assert_errno, create_tmp_dir, drop_rights, fd_get_rights, open_scratch_directory,
};

const TEST_FILENAME: &'static str = "file.cleanup";

unsafe fn test_fd_fdstat_set_rights(dir_fd: wasi::Fd) {
    let fd = wasi::path_open(
        dir_fd,
        0,
        TEST_FILENAME,
        wasi::OFLAGS_CREAT,
        wasi::RIGHTS_FD_READ | wasi::RIGHTS_FD_WRITE | wasi::RIGHTS_FD_SEEK | wasi::RIGHTS_FD_TELL,
        0,
        0,
    )
    .expect("creating a new file");

    // Ensure we can read and write to the file with sufficient rights
    let contents = &mut [0u8, 1, 2, 3];
    let ciovec = wasi::Ciovec {
        buf: contents.as_ptr() as *const _,
        buf_len: contents.len(),
    };

    wasi::fd_write(fd, &[ciovec]).expect("failed to write to file");

    let read_contents = &mut [0u8; 4];
    let iovec = wasi::Iovec {
        buf: read_contents.as_mut_ptr() as *mut _,
        buf_len: read_contents.len(),
    };

    wasi::fd_seek(fd, 0, wasi::WHENCE_SET).expect("seeking file to beginning");

    assert_eq!(
        wasi::fd_read(fd, &[iovec]).expect("failed to read file"),
        read_contents.len(),
        "Read fewer than expected bytes from file"
    );

    assert_eq!(contents, read_contents, "written bytes equal read bytes");

    let rights_to_drop = wasi::RIGHTS_FD_READ | wasi::RIGHTS_FD_WRITE;

    drop_rights(fd, rights_to_drop, 0);

    let (modified_rights, _) = fd_get_rights(fd);

    assert_eq!(
        modified_rights & rights_to_drop,
        0,
        "base rights should not have FD_READ | FD_WRITE"
    );

    assert_ne!(
        modified_rights & wasi::RIGHTS_FD_SEEK,
        0,
        "base rights should have FD_SEEK"
    );

    // Now check that reading/writing fails since we don't have sufficient rights anymore
    assert_errno!(
        wasi::fd_read(fd, &[iovec]).expect_err("fd_read succeeded with insufficient rights"),
        wasi::ERRNO_BADF,
        wasi::ERRNO_NOTCAPABLE
    );
    assert_errno!(
        wasi::fd_write(fd, &[ciovec]).expect_err("fd_write succeeded with insufficient rights"),
        wasi::ERRNO_BADF,
        wasi::ERRNO_NOTCAPABLE
    );

    // Check that attempting to regrant the original rights fails
    let fd_stat = wasi::fd_fdstat_get(fd).expect("fd_fdstat_get failed");
    let additional_rights =
        wasi::RIGHTS_FD_READ | wasi::RIGHTS_FD_WRITE | wasi::RIGHTS_FD_SEEK | wasi::RIGHTS_FD_TELL;

    assert_errno!(
        wasi::fd_fdstat_set_rights(
            fd,
            fd_stat.fs_rights_base | additional_rights,
            fd_stat.fs_rights_inheriting | additional_rights,
        )
        .expect_err("granting additional rights to an fd should fail"),
        wasi::ERRNO_NOTCAPABLE
    );

    // Cleanup
    wasi::fd_close(fd).expect("closing fd");
    wasi::path_unlink_file(dir_fd, TEST_FILENAME).expect("failed to remove file");
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

    const DIR_NAME: &str = "rights_dir.cleanup";
    let dir_fd;
    unsafe {
        dir_fd = create_tmp_dir(base_dir_fd, DIR_NAME);
    }

    // Run the tests.
    unsafe { test_fd_fdstat_set_rights(dir_fd) }

    unsafe { wasi::path_remove_directory(base_dir_fd, DIR_NAME).expect("failed to remove dir") }
}
