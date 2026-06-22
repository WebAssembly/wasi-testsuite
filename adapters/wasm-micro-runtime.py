import subprocess
import os
import shlex
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import importlib


# shlex.split() splits according to shell quoting rules.
# Use posix=False on Windows to preserve backslash path separators.
IWASM = shlex.split(os.getenv("IWASM", "iwasm"), posix=(os.name != "nt"))


def get_name() -> str:
    return "wamr"


def get_version() -> str:
    # ensure no args when version is queried
    result = subprocess.run(IWASM + ["--version"],
                            encoding="UTF-8", capture_output=True,
                            check=True)
    output = result.stdout.splitlines()[0].split(" ")
    return output[1]


def get_wasi_versions() -> List[str]:
    return ["wasm32-wasip1"]


def get_wasi_worlds() -> List[str]:
    return ["wasi:cli/command"]


def compute_argv(test_path: str,
                 args_env_root: Tuple[List[str], Dict[str, str], Optional[str]],
                 proposals: List[str],
                 wasi_world: str,
                 wasi_version: str) -> List[str]:

    argv = []
    argv += IWASM
    args, env, root = args_env_root

    for k, v in env.items():
        argv += ["--env", f"{k}={v}"]

    if root:
        argv += [f"--map-dir=/::{root}"]  # noqa: E231

    argv += [test_path]

    argv += args
    return argv
