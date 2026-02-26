import subprocess
import os
import shlex
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import importlib


# shlex.split() splits according to shell quoting rules
WAZERO = shlex.split(os.getenv("WAZERO", "wazero"))


def get_name() -> str:
    return "wazero"


def get_version() -> str:
    # ensure no args when version is queried
    result = subprocess.run(WAZERO[0:1] + ["version"],
                            encoding="UTF-8", capture_output=True,
                            check=True)
    version = result.stdout.strip()
    if version == "dev":
        version = "0.0.0"
    return version


def get_wasi_versions() -> List[str]:
    return ["wasm32-wasip1"]


def get_wasi_worlds() -> List[str]:
    return ["wasi:cli/command"]


def compute_argv(test_path: str,
                 args_env_dirs: Tuple[List[str], Dict[str, str], List[Tuple[Path, str]]],
                 proposals: List[str],
                 wasi_world: str,
                 wasi_version: str) -> List[str]:

    argv = []
    argv += WAZERO
    argv += ["run", "-hostlogging=filesystem"]
    args, env, dirs = args_env_dirs

    for k, v in env.items():
        argv += [f"-env={k}={v}"]

    for host, guest in dirs:
        argv += [f"-mount={host}:{guest}"]

    argv += [test_path]

    argv += args
    return argv
