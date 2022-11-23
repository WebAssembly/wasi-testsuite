import logging
import json
from typing import List, NamedTuple, TypeVar, Type, Dict, Any, Optional


class Output(NamedTuple):
    exit_code: int
    stdout: str
    stderr: str


class Failure(NamedTuple):
    type: str
    message: str


class Result(NamedTuple):
    output: Output
    is_executed: bool
    failures: List[Failure]

    @property
    def failed(self) -> bool:
        return len(self.failures) > 0


T = TypeVar("T", bound="Config")


class Config(NamedTuple):
    args: List[str] = []
    env: Dict[str, str] = {}
    exit_code: int = 0
    dirs: List[str] = []
    stdout: Optional[str] = None
    wasi_functions: List[str] = []

    @classmethod
    def from_file(cls: Type[T], config_file: str) -> T:
        default = cls()

        with open(config_file, encoding="utf-8") as file:
            dict_config = json.load(file)

        cls._validate_dict(dict_config)

        return cls(
            args=dict_config.get("args", default.args),
            env=dict_config.get("env", default.env),
            exit_code=dict_config.get("exit_code", default.exit_code),
            dirs=dict_config.get("dirs", default.dirs),
            wasi_functions=dict_config.get("wasi_functions", default.wasi_functions),
            stdout=dict_config.get("stdout", default.stdout),
        )

    @classmethod
    def _validate_dict(cls: Type[T], dict_config: Dict[str, Any]) -> None:
        for field_name in dict_config:
            if field_name not in cls._fields:
                logging.warning("Unknown field in the config file: %s", field_name)


class TestCase(NamedTuple):
    name: str
    config: Config
    result: Result
    duration_s: float
