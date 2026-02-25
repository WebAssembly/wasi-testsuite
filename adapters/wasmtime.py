import os
import shlex
import subprocess
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


def get_wasi_versions() -> List[str]:
    return ["wasm32-wasip1", "wasm32-wasip3"]


def compute_argv(test_path: str,
                 args_env_dirs: Tuple[List[str], Dict[str, str], List[Tuple[Path, str]]],
                 proposals: List[str],
                 wasi_version: str) -> List[str]:

    argv = []
    argv += WASMTIME
    args, env, dirs = args_env_dirs

    for k, v in env.items():
        argv += ["--env", f"{k}={v}"]

    for host, guest in dirs:
        argv += ["--dir", f"{host}::{guest}"]  # noqa: E231

    argv += [test_path]

    argv += args
    _add_wasi_version_options(argv, wasi_version, proposals)
    return argv


# The user might provide WASMTIME="wasmtime --option -Sfoo".  Let's
# insert the options to choose the WASI version before the user's
# options, so that the user can override our choices.
def _add_wasi_version_options(argv: List[str], wasi_version: str, proposals: List[str]) -> None:
    splice_pos = len(WASMTIME)
    while splice_pos > 1 and argv[splice_pos - 1].startswith("-"):
        splice_pos -= 1
    match wasi_version:
        case "wasm32-wasip1":
            pass
        case "wasm32-wasip3":
            flags_from_proposals = ""
            if "http" in proposals:
                flags_from_proposals += ",http"
            if "sockets" in proposals:
                flags_from_proposals += ",inherit-network"
            if "http/service" in proposals:
                flags_from_proposals += ",cli"
                argv[splice_pos:splice_pos] = ["serve", "--addr=127.0.0.1:0"]
                splice_pos += 1

            argv[splice_pos:splice_pos] = ["-Wcomponent-model-async",
                                           f"-Sp3{flags_from_proposals}"]

        case _:
            pass
