import {
    environ_sizes_get,
    environ_get,
    errno,
} from "@assemblyscript/wasi-shim/assembly/bindings/wasi_snapshot_preview1";

const dataBuf = memory.data(sizeof<usize>() * 2);

let err = environ_sizes_get(dataBuf, dataBuf + sizeof<usize>());
assert(err == errno.SUCCESS);

const expected = new Set<String>();
expected.add("a=text");
expected.add('b=escap " ing');
expected.add("c=new\nline");

const envCount = load<usize>(dataBuf);
assert(envCount == expected.size);

const dataSize = load<usize>(dataBuf, sizeof<usize>());
const ptrsSize = envCount * sizeof<usize>();
const envBufSize = ptrsSize + dataSize;
const envBuf = __alloc(envBufSize);

err = environ_get(envBuf, envBuf + ptrsSize);
assert(err == errno.SUCCESS);

for (let i = 0; i < <i32>envCount; ++i) {
    const ptr = load<usize>(envBuf + i * sizeof<usize>());
    const str = String.UTF8.decodeUnsafe(ptr, ptr + envBufSize - envBuf, true);
    assert(expected.has(str));
    expected.delete(str);
}
__free(envBuf);
