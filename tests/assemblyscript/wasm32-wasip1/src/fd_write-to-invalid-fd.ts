import { fd_write, errno } from "@assemblyscript/wasi-shim/assembly/bindings/wasi_snapshot_preview1";

const outSize = memory.data(sizeof<usize>());
const invalidFd = -31337;

const err = fd_write(invalidFd, 0, 0, outSize);

assert(err == errno.BADF);
