#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <unistd.h>

int main() {
  int a = open("fs-tests.dir/file", O_RDONLY);
  assert(a != -1);

  int b = open("fs-tests.dir/lseek.txt", O_RDONLY);
  assert(b != -1);

  struct stat a_stat;
  int a_r = fstat(a, &a_stat);
  assert(a_r == 0);

  struct stat b_stat;
  int b_r = fstat(b, &b_stat);
  assert(b_r == 0);

  // POSIX requires that `st_dev` and `st_ino` uniquely identify a file.
  // They're in the same directory and we assume there's nothing mounted
  // on top of them, so they should have the same `st_dev` value, which
  // means they need to have different `st_ino` values.
  assert(a_stat.st_dev == b_stat.st_dev);
  assert(a_stat.st_ino != b_stat.st_ino);

  return EXIT_SUCCESS;
}
