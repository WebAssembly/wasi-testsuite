import argparse
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--version', action='store_true')
parser.add_argument('--test-file', action='store')
parser.add_argument('--arg', action='append', default=[])
parser.add_argument('--env', action='append', default=[])
parser.add_argument('--dir', action='append', default=[])

args = parser.parse_args()

if args.version:
    subprocess.run(['iwasm', '--version'])
    sys.exit(0)

TEST_FILE=args.test_file
PROG_ARGS=args.arg 
ENV_ARGS=[f'--env={i}' for i in args.env]
DIR_ARGS=[f'--dir={i}' for i in args.dir]

sys.exit(subprocess.run(["iwasm"] + ENV_ARGS + DIR_ARGS + [TEST_FILE] + PROG_ARGS).returncode)
