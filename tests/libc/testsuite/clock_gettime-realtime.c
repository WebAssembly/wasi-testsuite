#include <assert.h>
#include <stdlib.h>
#include <time.h>

int main() {
  struct timespec ts;

  assert(clock_gettime(CLOCK_REALTIME, &ts) == 0);

  return EXIT_SUCCESS;
}
