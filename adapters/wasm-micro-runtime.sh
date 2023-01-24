#!/bin/bash

# WARNING: this adapter assumes iwasm from the latest wasm-micro-runtime.
# Namely the change to propagate WASI exit code:
# https://github.com/bytecodealliance/wasm-micro-runtime/pull/1748

TEST_FILE=
ARGS=()
DIR=()
ENV=()

IWASM="${TEST_RUNTIME_EXE:-iwasm}"

while [[ $# -gt 0 ]]; do
    case $1 in
    --version)
        ${IWASM} --version
        exit 0
        ;;
    --test-file)
        TEST_FILE="$2"
        shift
        shift
        ;;
    --arg)
        ARGS+=("$2")
        shift
        shift
        ;;
    --dir)
        DIR+=("--dir=$2")
        shift
        shift
        ;;
    --env)
        ENV+=("--env=$2")
        shift
        shift
        ;;
    *)
        echo "Unknown option $1"
        exit 1
        ;;
    esac
done

${IWASM} "${DIR[@]}" "${ENV[@]}" ${TEST_FILE} "${ARGS[@]}"
