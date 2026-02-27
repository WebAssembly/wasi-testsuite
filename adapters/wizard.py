import subprocess
import os
import shlex
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import importlib


# shlex.split() splits according to shell quoting rules
WIZARD = shlex.split(os.getenv("WIZARD", "wizeng.x86-64-linux"))


def get_name() -> str:
    return "wizard"


def get_version() -> str:
    # ensure no args when version is queried
    output = ""
    try:
        result = subprocess.run(WIZARD[0:1] + ["--version"],
                                encoding="UTF-8", capture_output=True,
                                check=False)
        output = result.stdout;
    except subprocess.CalledProcessError as e:
        # https://github.com/titzer/wizard-engine/issues/483
        if e.returncode != 3:
            raise e
        output = result.stdout
    output = output.splitlines()[0].split(" ")
    return output[1]


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
    argv += WIZARD
    args, env, dirs = args_env_dirs

    for k, v in env.items():
        argv += [f"--env={k}={v}"]

    for host, guest in dirs:
        # FIXME: https://github.com/titzer/wizard-engine/issues/482
        argv += [f"--dir={host}"]

    argv += [test_path]

    argv += args
    return argv
