import { args_sizes_get, args_get, errno } from "@assemblyscript/wasi-shim/assembly/bindings/wasi_snapshot_preview1";

const dataBuf = memory.data(sizeof<usize>() * 2);

let err = args_sizes_get(dataBuf, dataBuf + sizeof<usize>());
assert(err == errno.SUCCESS);

const argCount = load<usize>(dataBuf);
assert(argCount == 4);

const dataSize = load<usize>(dataBuf, sizeof<usize>());
const ptrsSize = argCount * sizeof<usize>();
const argBufSize = ptrsSize + dataSize;
const argBuf = __alloc(argBufSize);

err = args_get(argBuf, argBuf + ptrsSize);
assert(err == errno.SUCCESS);

const expected = ["first", 'the "second" arg', "3"];

for (let i = 1; i < <i32>argCount; ++i) {
    const ptr = load<usize>(argBuf + i * sizeof<usize>());
    const str = String.UTF8.decodeUnsafe(ptr, ptr + argBufSize - argBuf, true);
    assert(str == expected[i - 1]);
}
__free(argBuf);
