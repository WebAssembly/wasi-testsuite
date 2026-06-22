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
a file, so the WASI module is going to need to start with a root
filesystem.  Make the directory, say call it `stat-working-dir`, as a
subfolder of the directory your test is in.  Then create a
`filesystem-stat-subtlety.json` in the test directory:

```json
{
  "operations": [
    {
	  "type": "run",
	  "root": "stat-working-dir"
	}
  ]
}
```

A `root` declaration in the `run` operation of a test's JSON file
preopens that directory as the WASI guest's root filesystem (`/`).

If you need to create a file, name it something that ends with
`.cleanup`, if possible, and ideally have the test case remove it at the
end.  But just in case, the test runner will delete files under a test's
`root` with names like that, both before and after running the test.


## Building tests

Finally, we need to build the test.  The repository uses Buck2 for this.
Install [Dotslash](https://dotslash-cli.com/docs/installation/) once, then run
the relevant build recipe:

```bash
just build-c
just build-rust p1
just build-rust p3
just build-asc
```

To build all Buck targets, run:

```bash
just build
```

To build the redistributable archive containing precompiled tests and the
runner, run:

```bash
just dist
```

Buck2 fetches the Rust toolchain (including the `wasm32-wasip1` and
`wasm32-wasip2` standard libraries), WASI SDK, Node/AssemblyScript, wasm-tools,
and runtime tooling through the Buck toolchain graph, so no local Rust
installation or `rustup target add` is required.

## Final notes

Sounds gnarly, and in a way it is: cross-compiling for multiple targets
from multiple languages has some necessary complexity.  When in doubt,
do like other tests.  When really in doubt, take a look to see what the
[CI workflows](../.github/workflows/ci.yml) do.  Finally, see
the [full test case specification](./specification.md) for full details
on the JSON test metadata format.  Good luck!
