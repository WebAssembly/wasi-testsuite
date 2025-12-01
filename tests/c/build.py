#!/usr/bin/env python3

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from math import inf

# shlex.split() splits according to shell quoting rules
CC = shlex.split(os.getenv("CC", "clang"))

parser = argparse.ArgumentParser()
parser.add_argument("--dry-run", action="store_true")
parser.add_argument("--verbose", action="store_true")

args = parser.parse_args()

SYSTEMS = ['wasm32']
VERSIONS = ['wasip1'] # + ['wasip2', 'wasip3']

def compute_target(system, version):
    return f"{system}-{version}"

BASE_DIR = Path(__file__).parent

def maybe_stat(path, default):
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return default

def needs_rebuild(dst, src):
    if maybe_stat(dst, 0) < src.stat().st_mtime:
        return True
    return (maybe_stat(dst.with_suffix(".json"), -1)
            < maybe_stat(src.with_suffix(".json"), -inf))

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

for system in SYSTEMS:
    for version in VERSIONS:
        target = compute_target(system, version)
        generic_sources = list((BASE_DIR / "src").glob("*.c"))
        target_sources = list((BASE_DIR / "src" / target).glob("*.c"))

        target_dir = BASE_DIR / "testsuite" / target
        mkdir_p(target_dir)
        target_args = [f"--target={compute_target(system, version)}"]

        write_manifest(target_dir / "manifest.json",
                       {'name': f"WASI C tests [{target}]"})

        for src in generic_sources + target_sources:
            dst = (target_dir / src.name).with_suffix(".wasm")
            if needs_rebuild(dst, src):
                print(f"building testsuite/{target}/{dst.name}")
                src_json = src.with_suffix(".json")
                if src_json.exists():
                    dst_json = dst.with_suffix(".json")
                    with src_json.open() as f:
                        for d in json.load(f).get('dirs', []):
                            cp_R(src.parent / d, dst.parent / d)
                    cp(src_json, dst_json)
                run(CC + target_args + [src] + ['-o'] + [dst])
