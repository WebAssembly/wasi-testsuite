import argparse
import subprocess
import sys
import os
import shlex

# shlex.split() splits according to shell quoting rules
WIZARD = shlex.split(os.getenv("TEST_RUNTIME_EXE", "wizeng.x86-64-linux"))

parser = argparse.ArgumentParser()
parser.add_argument("--version", action="store_true")
parser.add_argument("--test-file", action="store")
parser.add_argument("--arg", action="append", default=[])
parser.add_argument("--env", action="append", default=[])
parser.add_argument("--dir", action="append", default=[])

args = parser.parse_args()

if args.version:
    # ensure no args when version is queried
    subprocess.run(WIZARD[0:1] + ["-version"])
    sys.exit(0)

TEST_FILE = args.test_file
PROG_ARGS = args.arg
ENV_ARGS = None if len(args.env) == 0 else f'--env={",".join(args.env)}'
DIR_ARGS = None if len(args.dir) == 0 else f'--dir={",".join(args.dir)}'

r = subprocess.run([arg for arg in WIZARD + [ENV_ARGS, DIR_ARGS, TEST_FILE] + PROG_ARGS if arg])
sys.exit(r.returncode)
