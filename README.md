# `wasi-testsuite`

This repository contains tests for WebAssembly System Interface (WASI) and a test executor for running WASI tests against a selected WebAssembly runtime.

WASI is a modular collection of standardized APIs. Currently, WASI has not reached version 1.0
stability but a snapshot of experimental APIs does exist ([`wasi_snapshot_preview1`]). This
repository only holds tests of APIs included in this snapshot. It does not include tests for other
in-progress proposals or other experimental APIs, though the test executor can run tests from other repositories (e.g., see the [wasi-threads] tests).

[`wasi_snapshot_preview1`]: https://github.com/WebAssembly/WASI/blob/main/legacy/preview1/docs.md
[wasi-threads]: https://github.com/WebAssembly/wasi-threads/tree/main/test

The test executor matches execution output against a JSON specification. Writing your own test
executor is quite simple; see the [specification] document for the details and the reference Python
[implementation].

[specification]: doc/specification.md
[implementation]: ./test-runner

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
   python3 test-runner/wasi_test_runner.py                                                  \
      -t ./tests/assemblyscript/testsuite/ `# path to folders containing .wasm test files` \
         ./tests/c/testsuite/                                                              \
         ./tests/rust/testsuite/                                                           \
      -r adapters/wasmtime.py # path to a runtime adapter
   ```

Optionally you can specify test cases to skip with the `--exclude-filter` option.

```bash
python3 test-runner/wasi_test_runner.py                                                  \
    -t ./tests/assemblyscript/testsuite/ `# path to folders containing .wasm test files` \
       ./tests/c/testsuite/                                                              \
       ./tests/rust/testsuite/                                                           \
    --exclude-filter examples/skip.json                                                  \
    -r adapters/wasmtime.py # path to a runtime adapter
```

The default executable in the adapter used for test execution can be
overridden using `TEST_RUNTIME_EXE` variable. This only works with adapters defined in
[adapters/](adapters/), and might not work with 3rd party adapters.

```bash
TEST_RUNTIME_EXE="wasmtime --wasm-features all" python3 test-runner/wasi_test_runner.py                                                  \
    -t ./tests/assemblyscript/testsuite/ \
    -r adapters/wasmtime.py
```

## Contributing

All contributions are very welcome. Contributors can help with:

- adding or updating test cases,
- improving test execution and reporting,
- integrating with new WASM runtimes,

and many others. We appreciate both code contributions as well as suggestions and bug reports.

## Developer guide

Here is some additional information for developers who are willing to contribute.

### Directory structure

- [`test-runner`](test-runner) - test executor scripts.
- [`tests`](tests) - source code of WASI tests and build scripts. The folder contains subfolders for all supported languages.
- [`.github`](.github) - CI workflow definitions.
- [`doc`](doc) - additional documentation.

### Cleaning up temporary resources

Some of the tests (e.g. [pwrite-with-access](./tests/c/testsuite/pwrite-with-access.c)) generate
output artifacts and their existence can affect consecutive test executions. Tests should clean up
the artifacts they generate, but there might be cases where the test fails early. The test runner
will automatically delete all the files and directories in the test suite directory with the
`.cleanup` suffix.

### Programming languages for tests

The repository currently consists of tests implemented in the following languages:

- `C` (with [`wasi-libc`](https://github.com/WebAssembly/wasi-libc))
- `AssemblyScript`
- `Rust`

The list of supported languages can be extended if needed.

### Branch structure

Apart from development branches for various features, we identify the following branches as critical (i.e. they won't be removed or force-updated):

- `main` - main branch of the repository. Use this branch for development (e.g. updating test cases, modifying test runner)
- `prod/testsuite-base` - the branch is an up-to-date fork of the `main` branch but it also includes precompiled binaries. Use this branch for simply running tests and validating WASM runtimes (see [doc](doc/precompiled-binaries.md) for details).
- `prod/daily-test-results` - the branch contains daily test results for supported WASM runtimes (at the moment, we only execute tests on wasmtime and WAMR). In the future we intend to publish those results to the website to provide users with additional input for selecting the runtime.
