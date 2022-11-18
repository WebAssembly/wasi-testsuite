import subprocess

from typing import Dict, NamedTuple, List

from .test_case import Output


class RuntimeVersion(NamedTuple):
    name: str
    version: str


class RuntimeAdapter:
    def __init__(self, adapter_path: str) -> None:
        self._adapter_path = adapter_path

    def get_version(self) -> RuntimeVersion:
        output = (
            subprocess.check_output([self._adapter_path, "--version"], encoding="UTF-8")
            .strip()
            .split(" ")
        )
        return RuntimeVersion(output[0], output[1])

    def run_test(
        self, test_path: str, args: List[str], env_variables: Dict[str, str]
    ) -> Output:
        args = (
            [
                self._adapter_path,
                "--test-file",
                test_path,
            ]
            + [a for arg in args for a in ("--args", arg)]
            + [e for env in self._env_to_list(env_variables) for e in ("--env", env)]
        )
        result = subprocess.run(args, capture_output=True, text=True, check=False)
        return Output(result.returncode, result.stdout, result.stderr)

    @staticmethod
    def _env_to_list(env: Dict[str, str]) -> List[str]:
        return [f"{key}={value}" for key, value in env.items()]
