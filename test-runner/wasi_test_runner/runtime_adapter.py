import subprocess
import sys
from pathlib import Path
from typing import Dict, NamedTuple, List

from .test_case import Output


class RuntimeVersion(NamedTuple):
    name: str
    version: str


class RuntimeAdapter:
    def __init__(self, adapter_path: str) -> None:
        self._adapter_path = self._abs(adapter_path)

    def get_version(self) -> RuntimeVersion:
        output = (
            subprocess.check_output([sys.executable, self._adapter_path, "--version"], encoding="UTF-8")
            .strip()
            .split(" ")
        )
        return RuntimeVersion(output[0], output[1])

    def run_test(
        self,
        test_path: str,
        args: List[str],
        env_variables: Dict[str, str],
        dirs: List[str],
    ) -> Output:
        args = (
            [
                sys.executable,
                self._adapter_path,
                "--test-file",
                self._abs(test_path),
            ]
            + [a for arg in args for a in ("--arg", arg)]
            + [d for dir in dirs for d in ("--dir", dir)]
            + [e for env in self._env_to_list(env_variables) for e in ("--env", env)]
        )

        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=False,
            cwd=Path(test_path).parent,
        )
        return Output(result.returncode, result.stdout, result.stderr)

    @staticmethod
    def _abs(path: str) -> str:
        return str(Path(path).absolute())

    @staticmethod
    def _env_to_list(env: Dict[str, str]) -> List[str]:
        return [f"{key}={value}" for key, value in env.items()]
