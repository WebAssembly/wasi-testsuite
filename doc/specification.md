# Test Specification

This document describes how to use the JSON test specifications to write your own test executor for
[`wasi-testsuite`](..). The test executor included in this project provides a completely-usable
reference [implementation](../test-runner), but projects with other requirements may want to run the
tests in their own way (e.g., no Python dependency). The JSON test specifications provide a simple
way to verify that the tests indeed passed.

### Execution Preparation

Before executing the tests, a test executor is expected to:

- Find all `*.wasm` files in a given subdirectory &mdash; these are the _test cases_
- Find all `*.cleanup` files in a given subdirectory and remove them &mdash; these are test
  artifacts that can be generated during testing
- For each test case, look for a `.json` file in the same directory matching the base name (e.g.,
  `foo.json` for `foo.wasm`) &mdash; parse this _specification_
- If no `.json` file is present, use a default specification.

### Configuration Spec

The included test executor supports two configuration specifications:
a legacy specification and a newer specification, referred to as
operation-based specification.

These are the default values for the legacy configuration specification:

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

In case a partial configuration is provided, default values will be
used.

The motivation for introducing the operation-based configuration
specification is to enable fine-grained control over the description
and expectations of each of the steps of each test, especially those
in which there is a need to describe interactions between a client and
a server e.g., sockets.

The general structure of the configuration specification is:

```json
{
  "proposals": []
  "operations": []
}
```

Where 

- `proposals` is a list of strings representing the proposals that
   must be enabled by each adapter to ensure the test's completion.
   Currently the `http` and `sockets` proposals are supported.
- `operations`: a list of operations to be sequentially validated and
  executed. The format of each operation is described below.


#### `run`

Defines how to start the execution of the test case.

**Fields:**
- `args` (optional): List of command-line arguments to pass to the WASI program
- `env` (optional): Dictionary of environment variables (key-value pairs)
- `dirs` (optional): List of directory paths to preopen

**Default values:**
```json
{
  "type": "run",
  "args": [],
  "env": {},
  "dirs": []
}
```

##### `wait`

Waits for the test case to complete and validates the exit code.

**Fields:**
- `exit_code` (optional): Expected exit code

**Default values:**
```json
{
  "type": "wait",
  "exit_code": 0
}
```

##### `read`

Reads and validates output from a stream (stdout or stderr).

**Fields:**
- `id` (optional): Stream identifier (`"stdout"` or `"stderr"`)
- `payload` (optional): Expected output content

**Default values:**
```json
{
  "type": "read",
  "id": "stdout",
  "payload": ""
}
```

##### `connect`

Establishes a connection to a server for network-based tests.

**Fields:**
- `id` (optional): Connection identifier for referencing in later operations
- `protocol_type` (optional): Protocol type (`"tcp"`, `"udp"`, or `"http"`)

**Default values:**
```json
{
  "type": "connect",
  "id": "server",
  "protocol_type": "tcp"
}
```

#### `send`

Sends data over a previously established connection.

**Fields:**
- `id` (required): Connection identifier to send on
- `payload` (optional): Data to send

**Default values:**
```json
{
  "type": "send",
  "id": "<required>",
  "payload": ""
}
```

##### `recv`

Receives and validates data from a previously established connection.

**Fields:**
- `id` (required): Connection identifier to receive on
- `payload` (optional): Expected received data

**Default values:**
```json
{
  "type": "recv",
  "id": "<required>",
  "payload": ""
}
```


When no operations are specified in the JSON file, the following default is used:

```json
{
  "operations": [
    {"type": "run"},
    {"type": "wait"}
  ]
}
```

### Specification Validation

The test executor enforces the following rules during configuration validation:

1. Each `run` operation must be paired with a `wait` operation
2. `read`, `connect`, `send`, and `recv` operations must come after a `run` operation
3. Connection IDs used in `connect` operations must be unique
4. Connection IDs referenced in `send` and `recv` operations must be previously defined in a `connect` operation

### Execution

It's important to note that although both the legacy configuration
specification and the operation-based configuration specification are
supported, the included test executor will convert the legacy
configuration to the operation-based configuration prior to test
execution. The legacy configuration can be described in terms of
`run`, `read` and `wait` operations.

Newer tests, or tests which require enabling specific proposals (e.g.,
`http`) will adopt the operation-based specification, therefore we
encourage external runners to adopt the operation-based specification.

To execute the tests, the test executor is expected to:
- `env`: construct an environment from each key-value pair in `env`; the environment should only
  contain these keys and otherwise should be empty (note that this environment is the WASI
  environment, whether the engine inherits the shell environment or explicitly configures it via
  `--env` parameters)
- `dir`: add each path listed in `dir` as WASI preopen directories (some engines use a `--dir`
  flag)
- `args`: pass each argument in order to the WASI program (most CLI engines allow appending these
  after the module path)
- `proposals`: pass the right flags to enable each WASI proposal.

The test executor runs the WebAssembly test case with the above context and records its results.

### Checking

After each operation is executed, the test executor validates the
operation's expectations. If the actual results don't match the
expected values defined in the operation, the test executor records a
failure for that operation. 

A test case _passes_ if each operation's expectations are met.
