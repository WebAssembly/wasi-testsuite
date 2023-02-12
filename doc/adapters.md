# WASM Runtime Adapters

The test runner is designed to support different types of WebAssembly runtimes. Because the command line interface for WASM runtime is not standardized, every runtime can arbitrarily define how parameters should be passed to the runtime.

WASI test runner is designed to support as many WASM runtimes as possible, therefore runtime peculiarities aren't hardcoded in the runner.

In order to integrate WASM runtime with a test runner, the user has to provide a `runtime adapter`. It's a *Python script* that takes command-line arguments and translates them to a runtime call. The reason for using a Python script over a generic "she-bang" executable, is to ensure cross-platform compatibility, such an executable is expected to be a python a script.

## Interface
The adapter executable must accept the following command line parameters and execute actions associated with those parameters:
* `--version` - prints to standard output name and version of the runtime in the following format: `<NAME> <VERSION>`
* `--env <NAME=VAL>` - passes environment variable to WASM module. The parameter can be used multiple times in one call.
* `--arg <ARG>` - passes argument `<ARG>` to WASM module. The parameter can be used multiple times in one call.
* `--dir <DIRECTORY>` - grants access to the `<DIRECTORY>` host directory. The parameter can be used multiple times in one call.
* `--test-file <PATH>` - runs WASM module located in `<PATH>`

The adapter must return exit code to the environment that was passed as an argument to the `proc_exit` function in WASM code. This can be verified by running the following code:

```wat
(module
 (import "wasi_snapshot_preview1" "proc_exit" (func $fimport$0 (param i32)))
 (memory $0 0)
 (export "memory" (memory $0))
 (export "_start" (func $0))
 (func $0
  (call $fimport$0
   (i32.const 13)
  )
 )
)
```
and check if the exit code is equal to `13`. There are also two test cases in Assembly Script test suite that verify the behavior:
* [proc_exit-failure](../tests/assemblyscript/testsuite/proc_exit-failure.ts)
* [proc_exit-success](../tests/assemblyscript/testsuite/proc_exit-success.ts)
### Examples:

Print runtime version:

```bash
$ ./adapter.py --version
wasmtime-cli 1.0.1
```

Run WASM module:

```bash
$ ./adapter.py --arg a1 --arg a2 --env E1=env1 --env E2=env2 --test-file test.wasm
# Expected to start test.wasm module with E1=env1 and E2=env2
# environment variables defined and arguments a1, a2 passed to
# the module.

$ echo $?
# should display value passed to proc_exit function in WASM code
```

## Examples

See the [`adapters`](../adapters) directory for example adapters.

## Contributions

We prefer runtime maintainers to maintain adapters in their own repository We'll only maintain adapters for [Bytecode Alliance](https://bytecodealliance.org/) projects and we'll aim for compatibility with the most recent stable version.

We'll accept pull requests for new adapters in this repository, but we can't guarantee we'll have the capacity to maintain them (so they might stop working with the new runtime release).