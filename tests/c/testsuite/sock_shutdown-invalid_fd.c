#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>

int main() {
  int fd = 420;
  assert(shutdown(fd, SHUT_RD) != 0);
  assert(errno == EBADF);

  return EXIT_SUCCESS;
}
