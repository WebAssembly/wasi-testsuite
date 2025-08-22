#!/usr/bin/env python3

import argparse
import contextlib
import json
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--dry-run", action="store_true")
parser.add_argument("--verbose", action="store_true")

args = parser.parse_args()

TARGETS = ['wasm32-wasip1']
BASE_DIR = Path(__file__).parent

def run(argv):
    if args.verbose:
        print(shlex.join([str(x) for x in argv]))
    if not args.dry_run:
        r = subprocess.run(argv)
        if r.returncode != 0:
            sys.exit(r.returncode)

def cp(src, dst):
    if args.verbose:
        print(f"cp {src} {dst}")
    if not args.dry_run:
        shutil.copy(src, dst)

def cp_R(src, dst):
    if args.verbose:
        print(f"cp -R {src} {dst}")
    if not args.dry_run:
        shutil.copytree(src, dst, dirs_exist_ok=True)

def write_manifest(path, manifest):
    if args.verbose:
        print(f"writing {path}")
    if not args.dry_run:
        path.write_text(json.dumps(manifest))

def mkdir_p(path):
    if args.verbose:
        print(f"mkdir -p {path}")
    if not args.dry_run:
        path.mkdir(parents=True, exist_ok=True)

for target in TARGETS:
    with contextlib.chdir(BASE_DIR / target):
        run(["npm", "install"])
        run(["npm", "run", "prettier-format-check"])
        run(["npm", "run", "build"])

    src_dir = BASE_DIR / target / "src"
    obj_dir = src_dir
    dst_dir = BASE_DIR / "testsuite" / target
    mkdir_p(dst_dir)

    write_manifest(dst_dir / "manifest.json",
                   {'name': f"WASI Assemblyscript  tests [{target}]"})

    for src in src_dir.glob("*.ts"):
        obj = (obj_dir / src.name).with_suffix(".wasm")
        dst = (dst_dir / src.name).with_suffix(".wasm")
        cp(obj, dst)
        src_json = src.with_suffix(".json")
        if src_json.exists():
            cp(src_json, dst.with_suffix(".json"))
            with src_json.open() as f:
                for d in json.load(f).get('dirs', []):
                    cp_R(src.parent / d, dst.parent / d)
