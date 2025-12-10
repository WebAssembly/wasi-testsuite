#!/usr/bin/env python3

import argparse
import json
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--dry-run", action="store_true",
                    help="don't actually do anything; implies --verbose")
parser.add_argument("--verbose", action="store_true",
                    help="print commands to be executed")
parser.add_argument("--release", action="store_true",
                    help="build tests in release mode")
args = parser.parse_args()
if args.dry_run:
    args.verbose = True

CARGO = ['cargo']
SYSTEMS = ['wasm32']
VERSIONS = ['wasip1', 'wasip3']

def compute_target(system, version):
    return f"{system}-{version}"

def compute_build_target(system, version):
    if version == 'wasip3':
        # wasm32-wasip3 triple not yet supported.
        return compute_target(system, 'wasip2')
    return compute_target(system, version)

def compute_channel_for_version(version):
    # At the time of writing, the nightly channel is
    # needed in order to make everything work with
    # WASI p3
    if version == 'wasip3':
        return "+nightly"
    return "+stable"

BASE_DIR = Path(__file__).parent

def run(argv):
    command_line = shlex.join([str(x) for x in argv])
    if args.verbose:
        print(command_line)
    if not args.dry_run:
        r = subprocess.run(argv)
        if r.returncode != 0:
            print(f"command exited with status {r.returncode}: {command_line}",
                  file=sys.stderr)
            sys.exit(r.returncode)

def cp(src, dst):
    if args.verbose:
        print(f"cp {src} {dst}")
    if not args.dry_run:
        shutil.copy(src, dst)

def rm_rf(dst):
    if args.verbose:
        print(f"rm -rf {dst}")
    if not args.dry_run:
        if dst.exists():
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()

ALREADY_COPIED = {}
def cp_R(src, dst):
    if src in ALREADY_COPIED:
        return
    else:
        ALREADY_COPIED[src] = dst
    rm_rf(dst)
    if args.verbose:
        print(f"cp -R {src} {dst}")
    if not args.dry_run:
        shutil.copytree(src, dst, symlinks=True, ignore_dangling_symlinks=True,
                        dirs_exist_ok=True)

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
        build_target = compute_build_target(system, version)
        build_mode = "release" if args.release else "debug"
        channel = compute_channel_for_version(version)

        build_args = CARGO + [channel] + [
            "build",
            f"--manifest-path={BASE_DIR / target / 'Cargo.toml'}",
            f"--target={build_target}"
        ]
        if args.release:
            build_args.append("--release")
        run(build_args)

        obj_dir = BASE_DIR / target / "target" / build_target / build_mode
        src_dir = BASE_DIR / target / "src" / "bin"
        dst_dir = BASE_DIR / "testsuite" / target
        mkdir_p(dst_dir)

        write_manifest(dst_dir / "manifest.json",
                       {'name': f"WASI Rust tests [{target}]"})

        for src in src_dir.glob("*.rs"):
            obj = (obj_dir / src.name).with_suffix(".wasm")
            dst = (dst_dir / src.name).with_suffix(".wasm")
            cp(obj, dst)
            src_json = src.with_suffix(".json")
            if src_json.exists():
                cp(src_json, dst.with_suffix(".json"))
                with src_json.open() as f:
                    for d in json.load(f).get('dirs', []):
                        cp_R(src.parent / d, dst.parent / d)
