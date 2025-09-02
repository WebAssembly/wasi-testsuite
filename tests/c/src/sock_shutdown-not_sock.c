#include <assert.h>
#include <errno.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <unistd.h>

int main() {
  assert(shutdown(STDOUT_FILENO, SHUT_RD) != 0);
  assert(errno == ENOTSOCK);

  return EXIT_SUCCESS;
}
