import subprocess
import os
import shlex
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import importlib


_test_runner_path = Path(__file__).parent.parent / "test-runner"
if str(_test_runner_path) not in sys.path:
    sys.path.insert(0, str(_test_runner_path))

_test_case_module = importlib.import_module('wasi_test_runner.test_case')

# shlex.split() splits according to shell quoting rules
RUN_PYWASM = Path(__file__).parent.parent / "tools" / "run-pywasm"


def get_name() -> str:
    return "pywasm"


def get_version() -> str:
    # ensure no args when version is queried
    result = subprocess.run([RUN_PYWASM, "--version"],
                            encoding="UTF-8", capture_output=True,
                            check=True)
    output = result.stdout.splitlines()[0].split(" ")
    return output[1]


def get_wasi_versions() -> List[str]:
    return ["wasm32-wasip1"]

def compute_argv(test_path: str,
                 config: _test_case_module.Config,
                 wasi_version: str) -> List[str]:
    argv = []
    for op in config.operations:
        match op:
            case _test_case_module.Run(args, env, dirs):
                argv += [str(RUN_PYWASM)]
                for k, v in env.items():
                    argv += ["--env", f"{k}={v}"]
                for host, guest in dirs:
                    argv += ["--dir", f"{host}::{guest}"]  # noqa: E231
                argv += [test_path]
                argv += args
    return argv
