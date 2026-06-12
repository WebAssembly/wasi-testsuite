#!/usr/bin/env python3
"""Run a single Buck-built WASI test through wasi_test_runner."""

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from wasi_test_runner.harness import run_tests
from wasi_test_runner.runtime_adapter import RuntimeAdapter


def _copy_file(src: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _copy_tree(src: str, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, symlinks=True)


def _write_manifest(path: Path, name: str, version: str) -> None:
    manifest = {
        "name": name,
        "version": version,
    }
    path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")


def main() -> int:
    """Materialize a one-test suite and delegate execution to the runner."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--wasm", required=True)
    parser.add_argument("--test-name", required=True)
    parser.add_argument("--suite-name", required=True)
    parser.add_argument("--wasi-version", required=True)
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--config")
    parser.add_argument("--fixture-dir", nargs=2, action="append", default=[])
    parser.add_argument("--expectations")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="wasi-buck-test-") as tmp:
        suite_dir = Path(tmp)
        _write_manifest(suite_dir / "manifest.json", args.suite_name, args.wasi_version)
        _copy_file(args.wasm, suite_dir / f"{args.test_name}.wasm")

        if args.config:
            _copy_file(args.config, suite_dir / f"{args.test_name}.json")

        for guest_name, host_dir in args.fixture_dir:
            _copy_tree(host_dir, suite_dir / guest_name)

        runtime = RuntimeAdapter(Path(args.adapter))
        expectations = [Path(args.expectations)] if args.expectations else None
        return run_tests([runtime], [suite_dir], expectations, verbose=True)


if __name__ == "__main__":
    sys.exit(main())
