buck := env_var_or_default("BUCK2", "./buck2")

set shell := ["bash", "-o", "pipefail", "-c"]

default:
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

# Run the Buck2 first-slice Wasmtime tests.
test:
    {{buck}} test //tests:wasmtime

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
