#include <assert.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char **argv) {
  int ret;
  int fd;
  int offset = 0;
  const char *expected = "d-t";
  const int expected_len = strlen(expected);
  char read_buf[16];

  fd = open("fs-tests.dir/pread.txt", O_RDONLY);
  assert(fd > 0);

  do {
    ret = pread(fd, read_buf, expected_len - offset, 4 + offset);
    assert(ret > 0);
    offset += ret;
  } while (offset < expected_len);
  assert(strncmp(read_buf, expected, expected_len) == 0);

  ret = close(fd);
  assert(ret == 0);

  return EXIT_SUCCESS;
}