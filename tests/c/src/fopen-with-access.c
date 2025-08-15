#include <assert.h>
#include <stdio.h>
#include <stdlib.h>

int main() {
  FILE *file = fopen("fs-tests.dir/file", "r");

  assert(file != NULL);

  assert(0 == fclose(file));

  return EXIT_SUCCESS;
}
