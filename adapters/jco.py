import json
import os
import shlex
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional


# shlex.split() splits according to shell quoting rules.
# Use posix=False on Windows to preserve backslash path separators.
JCO = shlex.split(os.getenv("JCO", "jco"), posix=(os.name != "nt"))


def get_name() -> str:
    return "jco"


def get_version() -> str:
    result = subprocess.run(JCO + ["--version"],
                            encoding="UTF-8", capture_output=True,
                            check=True)
    return result.stdout.strip()


def get_wasi_versions() -> List[str]:
    return ["wasm32-wasip3"]


def get_wasi_worlds() -> List[str]:
    return ["wasi:cli/command"]


def get_timeout_seconds() -> float:
    # jco transpiles each component before executing it, so startup can exceed
    # the default runner timeout under concurrent Buck test execution.
    return 30


def compute_argv(test_path: str,
                 args_env_root: Tuple[List[str], Dict[str, str], Optional[str]],
                 proposals: List[str],
                 wasi_world: str,
                 wasi_version: str) -> List[str]:
    args, env, root = args_env_root
    preopens = []
    if root:
        preopens.append({
            "guest": "/",
            "host": str(root),
        })

    return JCO + [
        "--component", test_path,
        "--test-name", Path(test_path).name,
        "--args", json.dumps(args),
        "--env", json.dumps(env),
        "--preopens", json.dumps(preopens),
    ]
