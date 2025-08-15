#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main() {
  char buf[4];
  int fd;
  FILE *file;
  size_t size;

  file = fopen("fs-tests.dir/lseek.txt", "r");
  assert(file != NULL);

  fd = fileno(file);

  size = fread(&buf, 1, 4, file);
  assert(size == sizeof(buf));
  fflush(file);
  assert(lseek(fd, 0, SEEK_CUR) == 4);

  size = fread(&buf, 1, 1, file);
  assert(size == 1);
  fflush(file);
  assert(lseek(fd, 0, SEEK_CUR) == 5);

  assert(buf[0] == '4');

  assert(lseek(fd, 0, SEEK_SET) == 0);
  assert(lseek(fd, 0, SEEK_END) == 8);

  fclose(file);

  return EXIT_SUCCESS;
}
