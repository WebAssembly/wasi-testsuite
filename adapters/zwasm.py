import os
import shlex
import subprocess
from typing import Dict, List, Tuple, Optional

# shlex.split() splits according to shell quoting rules
ZWASM = shlex.split(os.getenv("ZWASM", "zwasm"), posix=os.name != "nt")


def get_name() -> str:
    return "zwasm"


def get_version() -> str:
    # ensure no args when version is queried
    result = subprocess.run(ZWASM[0:1] + ["--version"],
                            encoding="UTF-8", capture_output=True,
                            check=True)
    # "zwasm v2.5.0 (wasm: v3_0, wasi: p2, engine: both)"
    output = result.stdout.splitlines()[0].split(" ")
    return output[1].lstrip("v")


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
    # zwasm parses options per subcommand, so `run` goes directly after the
    # executable and ahead of anything the user put in ZWASM.
    argv += ZWASM[0:1] + ["run"] + ZWASM[1:]
    args, env, root = args_env_root

    for k, v in env.items():
        argv += ["--env", f"{k}={v}"]

    if root:
        argv += ["--dir", f"{root}:/"]  # noqa: E231

    argv += [test_path]

    argv += args
    return argv
