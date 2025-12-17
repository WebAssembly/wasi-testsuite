import logging
import json
from enum import StrEnum
from typing import List, NamedTuple, TypeVar, Type, Dict, Any, Optional


class WasiVersion(StrEnum):
    WASM32_WASIP1 = 'wasm32-wasip1'
    WASM32_WASIP2 = 'wasm32-wasip2'
    WASM32_WASIP3 = 'wasm32-wasip3'


class Output(NamedTuple):
    exit_code: int
    stdout: str
    stderr: str
    response: str


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


class ProtocolType(StrEnum):
    TCP = 'tcp'
    UDP = 'udp'
    HTTP = 'http'


P = TypeVar("P", bound="Protocol")


class Protocol(NamedTuple):
    type: ProtocolType = ProtocolType("tcp")
    port: int = 3000
    address: str = "localhost"
    request: str = ""
    response: str = ""

    @classmethod
    def from_dict(cls: Type[P], cfg: Dict[str, Any]) -> P:
        logging.warning(cfg)
        default = cls()
        for field_name in cfg:
            if field_name not in cls._fields:
                logging.warning("Unknown field in the protocol configuration: %s", field_name)

        return cls(
            type=ProtocolType(cfg.get("type", default.type)),
            port=cfg.get("port", default.port),
            address=cfg.get("address", default.address),
            request=cfg.get("request", default.request),
            response=cfg.get("response", default.response),
        )


T = TypeVar("T", bound="Config")


class Config(NamedTuple):
    args: List[str] = []
    env: Dict[str, str] = {}
    exit_code: int = 0
    dirs: List[str] = []
    stdout: Optional[str] = None
    wasi_functions: List[str] = []
    protocol: Optional[Protocol] = None

    @classmethod
    def from_file(cls: Type[T], config_file: str) -> T:
        default = cls()

        with open(config_file, encoding="utf-8") as file:
            dict_config = json.load(file)

        cls._validate_dict(dict_config)

        protocol = None
        if dict_config.get("protocol") is not None:
            protocol = Protocol.from_dict(dict_config.get("protocol"))

        return cls(
            args=dict_config.get("args", default.args),
            env=dict_config.get("env", default.env),
            exit_code=dict_config.get("exit_code", default.exit_code),
            dirs=dict_config.get("dirs", default.dirs),
            wasi_functions=dict_config.get("wasi_functions", default.wasi_functions),
            stdout=dict_config.get("stdout", default.stdout),
            protocol=protocol
        )

    @classmethod
    def _validate_dict(cls: Type[T], dict_config: Dict[str, Any]) -> None:
        for field_name in dict_config:
            if field_name not in cls._fields:
                logging.warning("Unknown field in the config file: %s", field_name)


class TestCase(NamedTuple):
    name: str
    argv: List[str]
    config: Config
    result: Result
    duration_s: float
