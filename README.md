# `wasi-testsuite`

This repository contains tests for WebAssembly System Interface (WASI)
and a test executor for running WASI tests against a selected
WebAssembly runtime.

WASI is a modular collection of standardized APIs. Currently, WASI has
not reached version 1.0 stability; this repository contains tests for
[WASI preview
1](https://github.com/WebAssembly/WASI/blob/wasi-0.1/preview1/docs.md)
and the forthcoming [WASI preview
3](https://wasi.dev/roadmap).

This repository does not include tests for other in-progress proposals
or other experimental APIs, though the test executor can run tests from
other repositories (e.g., see the [wasi-threads] tests).

[wasi-threads]: https://github.com/WebAssembly/wasi-threads/tree/main/test

## Getting started

1. Clone the repository; use the `prod/testsuite-base` branch as it already includes precompiled
   test binaries (see [branch structure](#branch-structure)):

   ```bash
   git clone --branch prod/testsuite-base https://github.com/WebAssembly/wasi-testsuite
   ```

2. Make sure there is already an adapter for the runtime in the [`adapters`](adapters) directory; if
   not, create one (see [the doc](doc/adapters.md) for details).

3. Install `python3` (e.g., on Ubuntu):

   ```bash
   sudo apt install python3 python3-pip
   ```

4. Install the test runner dependencies:

   ```bash
   python3 -m pip install -r test-runner/requirements.txt
   ```

5. Execute the test suites from this repository:

   ```bash
   ./run-tests
   ```

By default, the test runner will detect available WASI runtimes from
those available in [adapters/](adapters/), and will run tests on all
available runtimes.  Pass `--runtime` to instead use a specific runtime.

```
./run-tests --runtime adapters/wasmtime.py
```

Running tests will invoke the WASI runtime's binary in a subprocess:
`wasmtime` for `adapters/wasmtime.py`, `iwasm` for
`adapters/wasm-micro-runtime.py`, and so on.  These binaries can be
overridden by setting corresponding environment variables (`WASMTIME`,
`IWASM`, etc):

```
WASMTIME="wasmtime --wasm-features all" ./run-tests
```

Optionally you can specify test cases to skip with the `--exclude-filter` option.
Expectation files use TOML.

```bash
./run-tests --exclude-filter examples/skip.toml
```

```toml
version = 1

[[suite]]
name = "WASI Rust tests [wasm32-wasip3]"

# Optional human explanation.
[[suite.test]]
name = "unsupported-test"
action = "skip"
```

### Building and testing with Buck2

The main development workflow uses Buck2 to build tests from source and run
them through the existing test runner. CI runs the Buck2 workflow across the
supported operating systems.

Install [Dotslash](https://dotslash-cli.com/docs/installation/) once before
using the checked-in `./buck2` launcher, for example with `cargo install dotslash`.
Install the Rust WASI targets used by the Rust test suites:

```bash
rustup target add wasm32-wasip1 wasm32-wasip2
```

Run the main runtime suites with:

```bash
just test
just test-jco
```

Additional runtime suites are available with:

```bash
just test-extra-runtimes
```

To build all Buck targets, run:

```bash
just build
```

Build the Buck-produced test data archive with:

```bash
just dist
```

The archive includes the test runner, adapters, Python requirements, and Buck built
test data. It can be run like this:

```bash
# Extract:
mkdir -p dist
tar -xzf buck-out/.../wasi-testsuite.tar.gz -C dist
# Set up Python:
python3 -m venv dist/venv
dist/venv/bin/python -m pip install -r dist/wasi-testsuite/test-runner/requirements.txt
# Run:
cd dist/wasi-testsuite
WASMTIME=/path/to/wasmtime ../venv/bin/python ./run-tests --runtime-adapter adapters/wasmtime.py
```

The same targets can be invoked directly with `./buck2`:

```bash
./buck2 test //tests:wasmtime
./buck2 test //tests:jco
./buck2 build --show-output //tests:dist
```

The Buck2 lint helpers mirror the CI checks:

```bash
just lint-starlark
just lint-cxx
just lint-rust
```

Buck2 fetches the WASI SDK, Node/AssemblyScript, wasm-tools, and runtimes
through the Buck toolchain graph, then uses a generic `wasi_test` rule to invoke
`wasi_test_runner` for each Buck test target.

## Contributing

Want to add a new test?  [There's a doc for that!](doc/writing-tests.md)

Trying to run these tests using some external test harness?  [It's possible!](doc/specification.md)

Want to add support for a new WASI runtime?  [Yes please!](doc/adapters.md)

Just want to have a look at the tests?  [Over here!](tests/)

Otherwise, suggestions and bugs are very welcome, over on the [issue
tracker](https://github.com/WebAssembly/wasi-testsuite/issues).

## Developer guide

Here is some additional information for developers who need to manage
the test runner itself.

### Directory structure

- [`test-runner`](test-runner) - test executor scripts.
- [`tests`](tests) - source code, metadata, and Buck targets for WASI tests. The folder contains subfolders for all supported languages.
- [`.github`](.github) - CI workflow definitions.
- [`doc`](doc) - additional documentation.

### Branch structure

Apart from development branches for various features, we identify the following branches as critical (i.e. they won't be removed or force-updated):

- `main` - main branch of the repository. Use this branch for development (e.g. updating test cases, modifying test runner)
- `prod/testsuite-base` - the branch is an up-to-date fork of the `main` branch but it also includes precompiled binaries. Use this branch for simply running tests and validating WASM runtimes (see [doc](doc/precompiled-binaries.md) for details).
- `prod/daily-test-results` - the branch contains daily test results for supported WASM runtimes. In the future we intend to publish those results to the website to provide users with additional input for selecting the runtime.
