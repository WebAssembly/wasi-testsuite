#include <assert.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

int pwrite_full(int fd, const char *content, int len, int offset) {
  int ret;
  int written = 0;
  do {
    ret = pwrite(fd, content + written, len - written, offset + written);
    assert(ret > 0);
    written += ret;
  } while (written < len);

  return written;
}

int main(int argc, char **argv) {
  int ret;
  int written;
  int fd;
  struct stat buf;
  char *test_file = "fs-tests.dir/writeable/test_pwrite_pread.txt.cleanup";
  char *full_content = "very long text";
  int full_content_len = strlen(full_content);
  const char *sub_content = "test";
  char read_buf[16];

  /* make sure the test file doesn't exist */
  ret = access(test_file, F_OK);
  assert(ret != 0);

  fd = open(test_file, O_WRONLY | O_CREAT);
  assert(fd > 0);

  ret = pwrite_full(fd, full_content, strlen(full_content), 0);
  assert(ret == strlen(full_content));

  ret = pwrite_full(fd, sub_content, strlen(sub_content), 3);
  assert(ret == strlen(sub_content));

  ret = close(fd);
  assert(ret == 0);

  fd = open(test_file, O_RDONLY);
  assert(fd > 0);

  written = 0;
  do {
    ret = read(fd, read_buf + written, sizeof(read_buf) - written);
    assert(ret > 0);
    written += ret;
  } while (written < full_content_len);
  assert(ret == full_content_len);

  assert(strncmp("vertestng text", read_buf, full_content_len) == 0);

  ret = close(fd);
  assert(ret == 0);

  ret = remove(test_file);
  assert(ret == 0);

  return 0;
}