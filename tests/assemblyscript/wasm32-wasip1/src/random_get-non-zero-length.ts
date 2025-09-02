import { random_get, errno } from "@assemblyscript/wasi-shim/assembly/bindings/wasi_snapshot_preview1";

const bufSize = 32;
const buf = memory.data(bufSize);

assert(errno.SUCCESS == random_get(buf, bufSize));
