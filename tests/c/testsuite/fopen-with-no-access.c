#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>

int main() {
  FILE *file = fopen("fs-tests.dir/file", "r");

  assert(file == NULL);
  assert(errno == ENOTCAPABLE);

  return EXIT_SUCCESS;
}
