#!/bin/bash

for input in testsuite/*.ts; do
  output="testsuite/$(basename $input .ts).wasm"

  if [ "$input" -nt "$output" ]; then
    echo "Compiling $input"
    npm run asc --silent -- "$input" -o "$output"
  fi
done
