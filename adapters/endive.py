import os
import shlex
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional

RUNNER = Path(__file__).parent.parent / "tools" / "EndiveRunner.java"

# shlex.split() splits according to shell quoting rules.
# Use posix=False on Windows to preserve backslash path separators.
if "ENDIVE" in os.environ:
    ENDIVE = shlex.split(os.environ["ENDIVE"], posix=(os.name != "nt"))
else:
    ENDIVE = ["jbang", "--quiet", str(RUNNER)]


def get_name() -> str:
    return "endive"


def get_version() -> str:
    # ENDIVE is a launcher command (jbang or java -jar), so keep all of it.
    result = subprocess.run(ENDIVE + ["--version"],
                            encoding="UTF-8", capture_output=True,
                            check=True)
    # "endive 1.1.0"
    return result.stdout.splitlines()[0].split(" ")[-1]


def get_wasi_versions() -> List[str]:
    return ["wasm32-wasip1"]


def get_wasi_worlds() -> List[str]:
    return ["wasi:cli/command"]


def get_timeout_seconds() -> float:
    # Every test starts a JVM, which can exceed the default runner timeout.
    return 30


def compute_argv(test_path: str,
                 args_env_root: Tuple[List[str], Dict[str, str], Optional[str]],
                 proposals: List[str],
                 wasi_world: str,
                 wasi_version: str) -> List[str]:

    argv = []
    argv += ENDIVE
    args, env, root = args_env_root

    for k, v in env.items():
        argv += ["--env", f"{k}={v}"]

    if root:
        argv += ["--dir", f"{root}::/"]  # noqa: E231

    argv += [test_path]

    argv += args
    return argv
