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

def compute_cc_target(system, version):
    if version == 'wasip3':
        # wasm32-wasip3 triple not yet supported.
        return compute_target(system, 'wasip2')
    return compute_target(system, version)

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

for system in SYSTEMS:
    for version in VERSIONS:
        target = compute_target(system, version)
        generic_sources = list((BASE_DIR / "src").glob("*.c"))
        target_sources = list((BASE_DIR / "src" / target).glob("*.c"))

        target_dir = BASE_DIR / "testsuite" / target
        target_dir.mkdir(parents=True, exist_ok=True)
        target_args = [f"--target={compute_cc_target(system, version)}"]

        manifest = {'name': f"WASI C tests [{target}]"}
        Path(target_dir / "manifest.json").write_text(json.dumps(manifest))

        for src in generic_sources + target_sources:
            dst = (target_dir / src.name).with_suffix(".wasm")
            if needs_rebuild(dst, src):
                print(f"building testsuite/{target}/{dst.name}")
                src_json = src.with_suffix(".json")
                if src_json.exists():
                    dst_json = dst.with_suffix(".json")
                    with src_json.open() as f:
                        for d in json.load(f).get('dirs', []):
                            src_dir = src.parent / d
                            dst_dir = dst.parent / d
                            if args.verbose:
                                print(f"cp --recursive {src_dir} {dst_dir}")
                            if not args.dry_run:
                                shutil.copytree(src_dir, dst_dir,
                                                dirs_exist_ok=True)
                    if args.verbose:
                        print(f"cp {src_json} {dst_json}")
                    if not args.dry_run:
                        shutil.copy(src_json, dst_json)
                build_cmd = CC + target_args + [src] + ['-o'] + [dst]
                command_line = shlex.join([str(x) for x in build_cmd])
                if args.verbose:
                    print(command_line)
                if not args.dry_run:
                    r = subprocess.run(build_cmd)
                    if r.returncode != 0:
                        sys.exit(r.returncode)
