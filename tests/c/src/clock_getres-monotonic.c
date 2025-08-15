#include <assert.h>
#include <stdlib.h>
#include <time.h>

int main() {
  struct timespec ts;

  assert(clock_getres(CLOCK_MONOTONIC, &ts) == 0);

  return EXIT_SUCCESS;
}
