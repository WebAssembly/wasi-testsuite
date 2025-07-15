import argparse
import os
import sys

import pywasm  # pip install pywasm

parser = argparse.ArgumentParser()
parser.add_argument("--version", action="store_true")
parser.add_argument("--test-file", action="store")
parser.add_argument("--arg", action="append", default=[])
parser.add_argument("--env", action="append", default=[])
parser.add_argument("--dir", action="append", default=[])

args = parser.parse_args()

if args.version:
    print('pywasm: https://github.com/mohanson/pywasm/releases/latest')
    sys.exit(0)

runtime = pywasm.core.Runtime()
wasi = pywasm.wasi.Preview1(
    [os.path.basename(args.test_file)] + args.arg,
    {e: e for e in args.dir},
    dict([e.split('=') for e in args.env]),
)
wasi.bind(runtime)
exit = wasi.main(runtime, runtime.instance_from_file(args.test_file))
sys.exit(exit)
