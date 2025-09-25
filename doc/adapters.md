# WASM Runtime Support

The WASI test runner will try to run all tests against all WASI
implementations that it knows about.  Each test is run in a fresh
sub-process.  A *runtime adapter* is code to translate the test
parameters (wasm file location, exposed directories, environment
variables, and any command-line arguments) into a command line that can
be run.  The adapter also indicates to the test runner which WASI
versions are supported by a WASI runtime and what the version of the
runtime itself is.

The WASI test runner includes adapters for
[pywasm](https://github.com/mohanson/pywasm),
[wamr](https://bytecodealliance.github.io/wamr.dev/),
[wasmedge](https://wasmedge.org), [wasmtime](https://wasmtime.dev),
[wazero](https://wazero.io), and
[wizard](https://github.com/titzer/wizard-engine/).  Contributions of
adapters for other runtimes are welcome.

## Writing your own adapter

The adapter is a python file that the test runner will load as a module.
To create a new adapter, we recommend you take a look at
[`adapters/wasmtime.py`](../adapters/wasmtime.py).  As you can see,
currently we require that the module define `get_name`, `get_version`,
and `compute_argv` functions.

We encourage you to submit your adapter upstream: it's not much code and
probably we can manage to make changes to it if test runner internals
change.  Though we don't change internals too often, we don't intend for
internal Python API of the test runner to be stable for external use.
