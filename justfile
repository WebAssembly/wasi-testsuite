buck := env_var_or_default("BUCK2", "./buck2")

set shell := ["bash", "-o", "pipefail", "-c"]

_default:
    @just --list

# Pass arbitrary arguments through to buck2.
buck *args:
    {{buck}} {{args}}

# List Buck targets in the repository.
targets:
    {{buck}} targets //...

# Build all Buck targets in the repository.
build:
    {{buck}} build //...

# Build one C runtime suite.
build-c runtime="wasmtime":
    {{buck}} build //tests/c:{{runtime}}

# Build one AssemblyScript runtime suite.
build-asc runtime="wasmtime":
    {{buck}} build //tests/assemblyscript/wasm32-wasip1:{{runtime}}

# Build one Rust runtime suite. Use `p1` or `p3`.
build-rust wasi="p1" runtime="wasmtime":
    {{buck}} build //tests/rust/wasm32-wasi{{wasi}}:{{runtime}}

# Build the distribution archive.
dist:
    {{buck}} build --show-output //tests:dist

# Run the Wasmtime Buck tests.
test:
    {{buck}} test //tests:wasmtime

# Run one C runtime suite.
test-c runtime="wasmtime":
    {{buck}} test //tests/c:{{runtime}}

# Run one AssemblyScript runtime suite.
test-asc runtime="wasmtime":
    {{buck}} test //tests/assemblyscript/wasm32-wasip1:{{runtime}}

# Run one Rust runtime suite. Use `p1` or `p3`.
test-rust wasi="p1" runtime="wasmtime":
    {{buck}} test //tests/rust/wasm32-wasi{{wasi}}:{{runtime}}

# Run all Buck tests under //tests.
test-all:
    {{buck}} test //tests/...

# Run one Buck test target, e.g. `just test-one //tests/c:lseek_wasmtime`.
test-one target:
    {{buck}} test {{target}}

# Run every lint recipe.
lint: lint-starlark lint-cxx lint-rust

# Run Starlark lint on Buck/Starlark/BXL files.
lint-starlark:
    git ls-files ':(glob)**/BUCK' ':(glob)**/*.bzl' ':(glob)**/*.bxl' | xargs {{buck}} starlark lint

# Build C/C++ diagnostic subtargets and print their reports.
lint-cxx:
    {{buck}} bxl scripts/check.bxl:main -- --kind cxx --output check --target //... | xargs cat

# Run Clippy for Rust targets and print its reports.
lint-rust:
    {{buck}} bxl scripts/check.bxl:main -- --kind rust --output clippy.txt --target //... | xargs cat

# Remove Buck outputs.
clean:
    {{buck}} clean
