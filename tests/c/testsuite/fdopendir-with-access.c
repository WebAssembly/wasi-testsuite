#include <assert.h>
#include <dirent.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
  DIR *d;
  struct dirent *dp;
  int dfd;
  int expected[2] = {0};

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
    } else if (strncmp(dp->d_name, "file-1", 6) == 0) {
      expected[1] = 1;
    } else {
      assert(0); // unexpected file
    }
  }
  closedir(d);

  assert(expected[0] == 1);
  assert(expected[1] == 1);

  return EXIT_SUCCESS;
}
