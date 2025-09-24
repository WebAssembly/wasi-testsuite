import subprocess
import os
import shlex
from pathlib import Path
from typing import Dict, List, Tuple

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


def compute_argv(test_path: str,
                 args: List[str],
                 env: Dict[str, str],
                 dirs: List[Tuple[Path, str]]) -> List[str]:
    argv = [] + WIZARD
    for k, v in env.items():
        argv += [f"--env={k}={v}"]
    for host, guest in dirs:
        # FIXME: https://github.com/titzer/wizard-engine/issues/482
        argv += [f"--dir={host}"]
    argv += [test_path]
    argv += args
    return argv
