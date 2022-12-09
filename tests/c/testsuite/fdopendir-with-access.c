#include <assert.h>
#include <dirent.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
  DIR *d;
  struct dirent *dp;
  int dfd;
  int expected[2] = {0};
  ino_t inodes[2];

  dfd = open("fs-tests.dir/fopendir.dir", O_RDONLY | O_DIRECTORY);
  assert(dfd != -1);

  d = fdopendir((dfd));
  assert(d != NULL);

  while ((dp = readdir(d)) != NULL) {
    if (dp->d_name[0] == '.') {
      continue;
    }
    if (strncmp(dp->d_name, "file-0", 6) == 0) {
      expected[0] = 1;
      inodes[0] = dp->d_ino;
    } else if (strncmp(dp->d_name, "file-1", 6) == 0) {
      expected[1] = 1;
      inodes[1] = dp->d_ino;
    } else {
      assert(0); // unexpected file
    }

    // Ensure that `d_ino` matches what `fstatat`'s `st_ino` tells us.
    struct stat statbuf;
    if (fstatat(dfd, dp->d_name, &statbuf, AT_SYMLINK_NOFOLLOW) != 0) {
      assert(0);
    }
    assert(statbuf.st_ino == dp->d_ino);
  }
  closedir(d);

  assert(expected[0] == 1);
  assert(expected[1] == 1);
  assert(inodes[0] != inodes[1]);

  return EXIT_SUCCESS;
}
