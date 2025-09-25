import subprocess
import os
import shlex
from pathlib import Path
from typing import Dict, List, Tuple

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


def compute_argv(test_path: str,
                 args: List[str],
                 env: Dict[str, str],
                 dirs: List[Tuple[Path, str]],
                 wasi_version: str) -> List[str]:
    argv = WAZERO + ["run", "-hostlogging=filesystem"]
    for k, v in env.items():
        argv += [f"-env={k}={v}"]
    for host, guest in dirs:
        argv += [f"-mount={host}:{guest}"]
    argv += [test_path]
    argv += args
    return argv
