# WASI tests

This repository contains WebAssembly System Interface (WASI) tests and a test executor for running WASI tests on a selected WebAssembly runtime.

The repository only holds tests that have been included in the WASI, and it does not include tests for in-progress proposals or other experimental APIs. Test executor included in the repository can however be used to run tests defined for proposals along with tests defined in this repository.

## Getting started

1. Clone repository
Use `prod/testsuite-base` branch as it already includes precompiled test binaries (see [Branch structure](#branch-structure) paragraph).
```bash
git clone --branch prod/testsuite-base git@github.com:WebAssembly/wasi-testsuite.git
```
2. Make sure there's already an adapter for the runtime in the [`adapters`](adapters) directory; if not, create one (see [the doc](doc/adapters.md) for details).
3. Install python3
   1. Ubuntu
    ```
    $ sudo apt install python3 python3-pip
    ```
4. Install test runner dependencies:
```bash
python3 -m pip install -r test-runner/requirements.txt
```
5. Execute test suites from this repository
```bash
python3 test-runner/wasi_test_runner.py                                                  \
    -t ./tests/assemblyscript/testsuite/ `# path to folders containing .wasm test files` \
       ./tests/c/testsuite/                                                              \
    -r adapters/wasmtime.sh # path to a runtime adapter
```

## Contributing
All contributions are very welcome. Contributors can help with:

* adding or updating test cases,
* improving test execution and reporting,
* integrating with new WASM runtimes,

and many others. We appreciate both code contributions as well as suggestions and bug reports.

## Developer guide
Here is some additional information for developers who are willing to contribute.

### Directory structure
* [`test-runner`](test-runner) - test executor scripts.
* [`tests`](tests) - source code of WASI tests and build scripts. The folder contains subfolders for all supported languages.
* [`.github`](.github) - CI workflow definitions.
* [`doc`](doc) - additional documentation.

### Programming languages for tests
The repository currently consists of tests implemented in the following languages:
* `C` (with [`wasi-libc`](https://github.com/WebAssembly/wasi-libc))
* `AssemblyScript`.

The list of supported languages can be extended if needed.

### Branch structure
Apart from development branches for various features, we identify the following branches as critical (i.e. they won't be removed or force-updated):

* `main` - main branch of the repository. Use this branch for development (e.g. updating test cases, modifying test runner)
* `prod/testsuite-base` - the branch is an up-to-date fork of the `main` branch but it also includes precompiled binaries. Use this branch for simply running tests and validating WASM runtimes (see [doc](doc/precompiled-binaries.md) for details).