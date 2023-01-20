import { random_get, errno } from "@assemblyscript/wasi-shim/assembly/bindings/wasi_snapshot_preview1";

const bufSize = 0;
const buf = __alloc(bufSize);

assert(errno.SUCCESS == random_get(buf, bufSize));

__free(buf);
