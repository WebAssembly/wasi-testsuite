import subprocess
import os
import shlex
from pathlib import Path
from typing import Dict, List, Tuple

# shlex.split() splits according to shell quoting rules
WASMTIME = shlex.split(os.getenv("WASMTIME", "wasmtime"))


def get_name() -> str:
    return "wasmtime"


def get_version() -> str:
    # ensure no args when version is queried
    result = subprocess.run(WASMTIME[0:1] + ["--version"],
                            encoding="UTF-8", capture_output=True,
                            check=True)
    output = result.stdout.splitlines()[0].split(" ")
    return output[1]


def compute_argv(test_path: str,
                 args: List[str],
                 env: Dict[str, str],
                 dirs: List[Tuple[Path, str]]) -> List[str]:
    argv = [] + WASMTIME
    for k, v in env.items():
        argv += ["--env", f"{k}={v}"]
    for host, guest in dirs:
        argv += ["--dir", f"{host}::{guest}"]  # noqa: E231
    argv += [test_path]
    argv += args
    return argv
