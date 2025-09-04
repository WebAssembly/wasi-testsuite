#include <assert.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>

int main() {
  char buf[4];
  int fd;
  size_t size;

  fd = open("fs-tests.dir/pwrite.cleanup",
            O_CREAT | O_TRUNC | O_WRONLY | O_APPEND);
  assert(fd != -1);

  size = write(fd, buf, 2);
  assert(size == 2);

  // test if O_APPEND is working
  assert(lseek(fd, 0, SEEK_SET) == 0);
  size = write(fd, buf, 2);
  assert(size == 2);
  assert(lseek(fd, 0, SEEK_CUR) == 4);

  size = pwrite(fd, buf, 3, 0);
  assert(size == 3);

  // fd_pwrite shouldn't update the current offset. POSIX says it should write
  // at 0, Linux says it should write at the end with `O_APPEND`. Accept either.
  assert(lseek(fd, 0, SEEK_CUR) == 4);
  int end = lseek(fd, 0, SEEK_END);
  assert(end == 4 || end == 7);

  close(fd);

  return EXIT_SUCCESS;
}
