use std::{env, process};
use wasi_tests::{assert_errno, open_scratch_directory};

unsafe fn test_fd_dir_ops(dir_fd: wasi::Fd) {
    let stat = wasi::fd_filestat_get(dir_fd).expect("failed to fdstat");
    assert_eq!(stat.filetype, wasi::FILETYPE_DIRECTORY);

    let (pr_fd, pr_name_len) = (3..)
        .map_while(|fd| wasi::fd_prestat_get(fd).ok().map(|stat| (fd, stat)))
        .find_map(|(fd, wasi::Prestat { tag, u })| {
            (tag == wasi::PREOPENTYPE_DIR.raw()).then_some((fd, u.dir.pr_name_len))
        })
        .expect("failed to find preopen directory");

    let mut pr_name = vec![];
    assert_errno!(
        wasi::fd_prestat_dir_name(pr_fd, pr_name.as_mut_ptr(), 0)
            .expect_err("fd_prestat_dir_name error"),
        wasi::ERRNO_INVAL,
        wasi::ERRNO_NAMETOOLONG
    );

    // Test that passing a larger than necessary buffer works correctly
    let mut pr_name = vec![0; pr_name_len + 1];
    let r = wasi::fd_prestat_dir_name(pr_fd, pr_name.as_mut_ptr(), pr_name_len + 1);
    assert_eq!(r, Ok(()));

    let mut read_buf = vec![0; 128].into_boxed_slice();
    let iovec = wasi::Iovec {
        buf: read_buf.as_mut_ptr(),
        buf_len: read_buf.len(),
    };

    // On posix, this fails with ERRNO_ISDIR
    assert_errno!(
        wasi::fd_read(dir_fd, &[iovec]).expect_err("fd_read error"),
        wasi::ERRNO_ISDIR,
        wasi::ERRNO_BADF,
        wasi::ERRNO_NOTCAPABLE
    );

    // On posix, this fails with ERRNO_ISDIR
    assert_errno!(
        wasi::fd_pread(dir_fd, &[iovec], 0).expect_err("fd_pread error"),
        wasi::ERRNO_ISDIR,
        wasi::ERRNO_BADF,
        wasi::ERRNO_NOTCAPABLE
    );

    let write_buf = vec![0; 128].into_boxed_slice();
    let ciovec = wasi::Ciovec {
        buf: write_buf.as_ptr(),
        buf_len: write_buf.len(),
    };

    // On posix, this fails with ERRNO_ISDIR
    assert_errno!(
        wasi::fd_write(dir_fd, &[ciovec]).expect_err("fd_write error"),
        wasi::ERRNO_ISDIR,
        wasi::ERRNO_BADF,
        wasi::ERRNO_NOTCAPABLE
    );

    // On posix, this fails with ERRNO_ISDIR
    assert_errno!(
        wasi::fd_pwrite(dir_fd, &[ciovec], 0).expect_err("fd_pwrite error"),
        wasi::ERRNO_ISDIR,
        wasi::ERRNO_BADF,
        wasi::ERRNO_NOTCAPABLE
    );

    // Divergence from posix: lseek(dirfd) will return 0
    assert_errno!(
        wasi::fd_seek(dir_fd, 0, wasi::WHENCE_CUR).expect_err("fd_seek WHENCE_CUR error"),
        wasi::ERRNO_ISDIR,
        wasi::ERRNO_BADF,
        wasi::ERRNO_NOTCAPABLE
    );

    // Divergence from posix: lseek(dirfd) will return 0
    assert_errno!(
        wasi::fd_seek(dir_fd, 0, wasi::WHENCE_SET).expect_err("fd_seek WHENCE_SET error"),
        wasi::ERRNO_ISDIR,
        wasi::ERRNO_BADF,
        wasi::ERRNO_NOTCAPABLE
    );

    // Divergence from posix: lseek(dirfd) will return 0
    assert_errno!(
        wasi::fd_seek(dir_fd, 0, wasi::WHENCE_END).expect_err("fd_seek WHENCE_END error"),
        wasi::ERRNO_ISDIR,
        wasi::ERRNO_BADF,
        wasi::ERRNO_NOTCAPABLE
    );

    // Tell isnt in posix, its basically lseek with WHENCE_CUR above
    assert_errno!(
        wasi::fd_tell(dir_fd).expect_err("fd_tell error"),
        wasi::ERRNO_ISDIR,
        wasi::ERRNO_BADF,
        wasi::ERRNO_NOTCAPABLE
    );

    // fallocate(dirfd, FALLOC_FL_ZERO_RANGE, 0, 1) will fail with errno EBADF on linux.
    // not available on mac os.
    assert_errno!(
        wasi::fd_allocate(dir_fd, 0, 1).expect_err("fd_allocate error"),
        wasi::ERRNO_ISDIR,
        wasi::ERRNO_BADF,
        wasi::ERRNO_NOTCAPABLE
    );

    // ftruncate(dirfd, 1) will fail with errno EINVAL on posix.
    assert_errno!(
        wasi::fd_filestat_set_size(dir_fd, 0).expect_err("fd_filestat_set_size error"),
        wasi::ERRNO_ISDIR,
        wasi::ERRNO_INVAL,
        wasi::ERRNO_BADF,
        wasi::ERRNO_NOTCAPABLE
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
    let dir_fd = match open_scratch_directory(&arg) {
        Ok(dir_fd) => dir_fd,
        Err(err) => {
            eprintln!("{}", err);
            process::exit(1)
        }
    };

    unsafe {
        test_fd_dir_ops(dir_fd);
    }
}
