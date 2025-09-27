# Writing tests

So you want to contribute a test?  Great!  Here's a quick summary.

## Before you start

Firstly, what language are you going to use to write your test?  The
principal languages in which tests are authored are C and Rust, which
each have their own toolchain.  These tests are in
[`tests/c`](../tests/c/) and [`tests/rust`](../tests/rust/),
respectively.  We would be happy to add other WASI-targeting language
toolchains.

Secondly, what WASI version are you testing?  Currently the WASI test
suite has tests for WASI preview 1 (sometimes versioned as 0.1) and for
WASI preview 3 (version 0.3.0, currently in pre-releases), corresponding
to the `wasm32-wasip1` and `wasm32-wasip3` compiler targets.  (Adding
support for `wasm64` variants would be welcome.)  Tests written in C
typically target a standard POSIX API, leaving it up to the toolchain to
select the WASI version used for the resulting binary; for this reason
there is just one [`tests/c/src`](../tests/c/src) directory with all the
tests, which may be compiled for different WASI targets.  But different
WASI versions have different APIs, and Rust tests are typically coded
directly against them, with tests for the different versions in
different directories, e.g.
[`tests/rust/wasm32-wasip1`](../tests/rust/wasm32-wasip1) and
[`tests/rust/wasm32-wasip3`](../tests/rust/wasm32-wasip3).

## Make test source and (possibly) its JSON

Next, what are you testing?  Let's say you are testing some subtlety
regarding `stat`, for WASIp3, in Rust.  Well then you need to add your
`filesystem-stat-subtlety.rs` to
[`tests/rust/wasm32-wasip3/src/bin/`](../tests/rust/wasm32-wasip3/src/bin/),
and it will be automatically built.  (How?  We'll come back to that.)

What does your test need?  If you are testing `stat`, probably you need
a file, so the WASI module is going to need to start with a preopened
directory.  Make the directory, say call it `stat-working-dir`, as a
subfolder of the directory your test is in.  Then create a
`filesystem-stat-subtlety.json` in the test directory:

```json
{
  "dirs": ["stat-working-dir"]
}
```

A `dirs` declaration in a test's JSON file adds a dir to the preopens.

If you need to create a file, name it something that ends with
`.cleanup`, if possible, and ideally have the test case remove it at the
end.  But just in case, the test runner will delete files in a test's
`dirs` with names like that, both before and after running the test.


## Building tests

Finally, we need to build the test.  C tests are built by running
[`tests/c/build.py`](../tests/c/build.py), and Rust tests via
[`tests/rust/build.py`](../tests/rust/build.py).  Those scripts will
compile all the tests they have (all the <tt>tests/c/src/\*.c</tt> files
and all the <tt>tests/rust/<i>target</i>/src/bin/\*.rs</tt> files), and
copy the resulting wasm files to the generated build directory
(<tt>tests/c/testsuite/<i>target</i>/</tt> or
<tt>tests/rust/testsuite/<i>target</i>/</tt>).  `build.py` will also
copy directories if needed.  Pass `--verbose --dry-run` to the
`build.py` scripts to see what they are doing.

Of course, you need a toolchain for those build scripts to work.
Concretely, you need a toolchain from C or Rust that can target
`wasm32-wasip1` or `wasm32-wasip3`.

For C, one installs `wasi-sdk`.  On x64-64 Ubuntu, that gives us:

```
export WASI_SDK=wasi-sdk-27.0-x86_64-linux
curl -LO https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-27/$WASI_SDK.tar.gz
tar xvf $WASI_SDK.tar.gz
export WASI_SDK_PATH=`pwd`/$WASI_SDK
export CC="${WASI_SDK_PATH}/bin/clang"
export CXX="${WASI_SDK_PATH}/bin/clang++"
```

For Rust, one uses `cargo`.  Use [rustup](https://rustup.rs/):

```
rustup update
rustup toolchain install stable
rustup toolchain install nightly # needed for wasip3, for now
rustup default stable
rustup +stable target add wasm32-wasip1
rustup +nightly target add wasm32-wasip2 # for wasip3
```

Note that until wasip3 is released, we use the wasip2 toolchain for
wasip3.

Now you can run `build.py`.  For Rust, run as `./build.py
--toolchain=wasm32-wasip3:nightly`, so as to use the nightly channel
instead of the default stable, for wasip3.

## Final notes

Sounds gnarly, and in a way it is: cross-compiling for multiple targets
from multiple languages has some necessary complexity.  When in doubt,
do like other tests.  When really in doubt, take a look to see what the
[CI workflows](../.github/workflows/compile-tests.yml) do.  Finally, see
the [full test case specification](./specification.md) for full details
on the JSON test metadata format.  Good luck!
