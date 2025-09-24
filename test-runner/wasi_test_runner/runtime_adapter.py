import subprocess
import sys
from pathlib import Path
from typing import Dict, NamedTuple, List

from .test_case import Output


class RuntimeVersion(NamedTuple):
    name: str
    version: str

    def __str__(self) -> str:
        return f"{self.name} {self.version}"


class RuntimeAdapter:
    def __init__(self, adapter_path: str) -> None:
        self._adapter_path = adapter_path
        self._cached_version: RuntimeVersion | None = None

    def get_version(self) -> RuntimeVersion:
        if self._cached_version is None:
            argv = [sys.executable, self._adapter_path, "--version"]
            result = subprocess.run(argv, encoding="UTF-8", capture_output=True,
                                    check=True)
            output = result.stdout.strip().split(" ")
            self._cached_version = RuntimeVersion(output[0], output[1])
        return self._cached_version

    def compute_argv(self, test_path: str, args: List[str],
                     env_variables: Dict[str, str],
                     dirs: List[str]) -> List[str]:
        argv = [sys.executable, self._adapter_path]
        argv += ["--test-file", test_path]
        for d in dirs:
            argv += ["--dir", f"{Path(test_path).parent / d}::{d}"]  # noqa: E231
        for k, v in env_variables.items():
            argv += ["--env", f"{k}={v}"]
        for a in args:
            argv += ["--arg", a]
        return argv

    def run_test(self, argv: List[str]) -> Output:
        result = subprocess.run(argv, capture_output=True, text=True,
                                check=False)
        return Output(result.returncode, result.stdout, result.stderr)
