#!/bin/bash

TEST_FILE=
ARGS=()
ENV=()

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
        ARGS+=("$2")
        shift
        shift
        ;;
    --env)
        ENV+=("--env" "$2")
        shift
        shift
        ;;
    *)
        echo "Unknown option $1"
        exit 1
        ;;
    esac
done

wasmtime $TEST_FILE "${ENV[@]}" "${ARGS[@]}"