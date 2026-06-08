buck := env_var_or_default("BUCK2", "./buck2")

set shell := ["bash", "-o", "pipefail", "-c"]

_default:
    @just --list

# Pass arbitrary arguments through to buck2.
[group('meta')]
buck *args:
    {{buck}} {{args}}

# List Buck targets in the repository.
[group('meta')]
targets:
    {{buck}} targets //...

# Remove Buck outputs.
[group('meta')]
clean:
    {{buck}} clean

# Run every lint recipe.
[group('check')]
lint: lint-starlark lint-cxx lint-rust

# Run Starlark lint on Buck/Starlark/BXL files.
[group('check')]
lint-starlark:
    git ls-files ':(glob)**/BUCK' ':(glob)**/*.bzl' ':(glob)**/*.bxl' | xargs {{buck}} starlark lint

# Build C/C++ diagnostic subtargets and print their reports.
[group('check')]
lint-cxx:
    {{buck}} bxl scripts/check.bxl:main -- --kind cxx --output check --target //... | xargs cat

# Run Clippy for Rust targets and print its reports.
[group('check')]
lint-rust:
    {{buck}} bxl scripts/check.bxl:main -- --kind rust --output clippy.txt --target //... | xargs cat

# Build all Buck targets in the repository.
[group('build')]
build:
    {{buck}} build //...

# Build one C runtime suite.
[group('build')]
build-c runtime="wasmtime":
    {{buck}} build //tests/c:{{runtime}}

# Build one AssemblyScript runtime suite.
[group('build')]
build-asc runtime="wasmtime":
    {{buck}} build //tests/assemblyscript/wasm32-wasip1:{{runtime}}

# Build one Rust runtime suite. Use `p1` or `p3`.
[group('build')]
build-rust wasi="p1" runtime="wasmtime":
    {{buck}} build //tests/rust/wasm32-wasi{{wasi}}:{{runtime}}

# Build the distribution archive.
[group('package')]
dist:
    {{buck}} build --show-output //tests:dist

# Run the Wasmtime Buck tests.
[group('test')]
test:
    {{buck}} test //tests:wasmtime

# Run the jco Buck tests.
[group('test')]
test-jco:
    {{buck}} test //tests:jco

# Run one C runtime suite.
[group('test')]
test-c runtime="wasmtime":
    {{buck}} test //tests/c:{{runtime}}

# Run one AssemblyScript runtime suite.
[group('test')]
test-asc runtime="wasmtime":
    {{buck}} test //tests/assemblyscript/wasm32-wasip1:{{runtime}}

# Run one Rust runtime suite. Use `p1` or `p3`.
[group('test')]
test-rust wasi="p1" runtime="wasmtime":
    {{buck}} test //tests/rust/wasm32-wasi{{wasi}}:{{runtime}}

# Run all Buck tests under //tests.
[group('test')]
test-all:
    {{buck}} test //tests/...

# Run additional Buck runtime suites.
[group('test')]
test-extra-runtimes:
    {{buck}} test //tests:wazero //tests:wasmedge //tests:wamr

# Run one Buck test target, e.g. `just test-one //tests/c:lseek_wasmtime`.
[group('test')]
test-one target:
    {{buck}} test {{target}}
