#!/bin/bash

TEST_FILE=
ARGS=()
PROG_ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
    --version)
        wasmtime -V
        exit 0
        ;;
    --test-file)
        TEST_FILE="$2"
        shift
        shift
        ;;
    --arg)
        PROG_ARGS+=("$2")
        shift
        shift
        ;;
    --env)
        ARGS+=("--env" "$2")
        shift
        shift
        ;;
    --dir)
        ARGS+=("--dir" "$2")
        shift
        shift
        ;;
    *)
        echo "Unknown option $1"
        exit 1
        ;;
    esac
done

wasmtime $TEST_FILE "${PROG_ARGS[@]}" "${ARGS[@]}"