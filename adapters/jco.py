import subprocess
import os
import shlex
from pathlib import Path
from typing import Dict, List, Tuple

# shlex.split() splits according to shell quoting rules
JCO = shlex.split(os.getenv("JCO", "jco"))


def get_name() -> str:
    return "jco"


def get_version() -> str:
    result = subprocess.run(JCO + ["--version"],
                            encoding="UTF-8", capture_output=True,
                            check=True)
    return result.stdout.strip()


def get_wasi_versions() -> List[str]:
    return ["wasm32-wasip2", "wasm32-wasip3"]


def compute_argv(test_path: str,
                 args: List[str],
                 env: Dict[str, str],
                 dirs: List[Tuple[Path, str]],
                 wasi_version: str) -> List[str]:
    argv = [] + JCO
    argv += ["run"]
    for k, v in env.items():
        argv += ["--env", f"{k}={v}"]
    for host, guest in dirs:
        argv += ["--dir", f"{host}::{guest}"]  # noqa: E231
    argv += [test_path]
    argv += args
    return argv
