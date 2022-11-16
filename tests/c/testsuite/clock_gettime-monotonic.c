#include <assert.h>
#include <stdlib.h>
#include <time.h>

int main() {
  struct timespec ts1, ts2;

  assert(clock_gettime(CLOCK_MONOTONIC, &ts1) == 0);
  assert(clock_gettime(CLOCK_MONOTONIC, &ts2) == 0);

  if (ts1.tv_sec == ts2.tv_sec)
    assert(ts1.tv_nsec < ts2.tv_nsec);
  else
    assert(ts1.tv_sec < ts2.tv_sec);

  return EXIT_SUCCESS;
}
