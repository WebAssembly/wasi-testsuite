import subprocess
import os
import shlex
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import importlib


_test_runner_path = Path(__file__).parent.parent / "test-runner"
if str(_test_runner_path) not in sys.path:
    sys.path.insert(0, str(_test_runner_path))

_test_case_module = importlib.import_module('wasi_test_runner.test_case')

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


def compute_argv(test_path: str,
                 config: _test_case_module.Config,
                 wasi_version: str) -> List[str]:
    argv = []
    for op in config.operations:
        match op:
            case _test_case_module.Run(args, env, dirs):
                argv += [WIZARD]
                for k, v in env.items():
                    argv += [f"--env={k}={v}"]
                for host, guest in dirs:
                    # FIXME: https://github.com/titzer/wizard-engine/issues/482
                    argv += [f"--dir={host}"]
                argv += [test_path]
                argv += args
    return argv
