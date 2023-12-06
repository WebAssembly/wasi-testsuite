#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main() {
  char buf[4];
  int fd;
  FILE *file;
  size_t size;

  file = fopen("fs-tests.dir/pwrite.cleanup", "a+");
  assert(file != NULL);

  fd = fileno(file);

  size = fwrite(buf, 1, 4, file);
  assert(size == sizeof(buf));
  fflush(file);

  size = pwrite(fd, buf, 4, 0);
  assert(size == sizeof(buf));
  fflush(file);

  // fd_pwrite should write from offset 0 regardless of append.
  assert(lseek(fd, 0, SEEK_END) == 4);

  fclose(file);

  return EXIT_SUCCESS;
}
