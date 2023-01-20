import { environ_sizes_get, errno } from "@assemblyscript/wasi-shim/assembly/bindings/wasi_snapshot_preview1";

const buf = memory.data(sizeof<usize>());

const err = environ_sizes_get(buf, buf + sizeof<usize>());
assert(err == errno.SUCCESS);

const count = load<usize>(buf);
assert(count == 3);
