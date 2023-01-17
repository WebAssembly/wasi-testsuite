import { fd_write, iovec, errno } from "@assemblyscript/wasi-shim/assembly/bindings/wasi_snapshot_preview1";

const message = "hello";

const utf8len = <usize>String.UTF8.byteLength(message);
const utf8buf = __alloc(utf8len);

String.UTF8.encodeUnsafe(changetype<usize>(message), message.length, utf8buf);

const iov = memory.data(sizeof<iovec>());
store<u32>(iov, utf8buf, 0);
store<u32>(iov, utf8len, sizeof<usize>());

const outSize = memory.data(sizeof<usize>());

const err = fd_write(1, iov, 1, outSize);
__free(utf8buf);

assert(load<usize>(outSize) == message.length);

assert(err == errno.SUCCESS);
