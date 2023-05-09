# Test Specification

This document describes how to use the JSON test specifications to write your own test executor for
[`wasi-testsuite`](..). The test executor included in this project provides a completely-usable
reference [implementation](../test-runner), but projects with other requirements may want to run the
tests in their own way (e.g., no Python dependency). The JSON test specifications provide a simple
way to verify that the tests indeed passed.

### Configuration

Before executing anything, a test executor is expected to:
- find all `*.wasm` files in a given subdirectory &mdash; these are the _test cases_
- find all `*.cleanup` files in a given subdirectory and remove them &mdash; these are test
  artifacts that can be generated during testing
- for each test case, look for a `.json` file in the same directory matching the base name (e.g.,
  `foo.json` for `foo.wasm`) &mdash; parse this _specification_
- if no `.json` file is present, use a default specification; a (conceptual) default specification
  would look like:

  ```json
  {
    "args": [],
    "dirs": [],
    "env": {},
    "exit_code": 0,
    "stderr": "",
    "stdout": ""
  }
  ```

- if the specification is missing fields, use default values

### Execution

To execute the tests, the test executor is expected to:
- `env`: construct an environment from each key-value pair in `env`; the environment should only
  contain these keys and otherwise should be empty (note that this environment is the WASI
  environment, whether the engine inherits the shell environment or explicitly configures it via
  `--env` parameters)
- `dir`: add each path listed in `dir` as WASI preopen directories (some engines use a `--dir`
  flag)
- `args`: pass each argument in order to the WASI program (most CLI engines allow appending these
  after the module path)

The test executor runs the WebAssembly test case with the above context and records its results.

### Checking

With the execution results in hand, the test executor is expected to:
- `exit_code`: check that the WASI exit code matches `exit_code`, or `0` if none was provided
- `stderr`: if a `stderr` field is provided, check that the bytes printed to `stderr` match it
- `stdout`: if a `stdout` field is provided, check that the bytes printed to `stdout` match it

A test case _passes_ if all of the checks are true.
