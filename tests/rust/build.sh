#!/bin/bash
set -ueo pipefail

cargo build --target=wasm32-wasip1

cp target/wasm32-wasip1/debug/*.wasm testsuite/
