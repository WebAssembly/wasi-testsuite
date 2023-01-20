#!/bin/bash
set -ueo pipefail

cargo build --target=wasm32-wasi

cp target/wasm32-wasi/debug/*.wasm testsuite/