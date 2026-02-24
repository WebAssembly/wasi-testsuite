import logging
import json
from pathlib import Path
from enum import StrEnum
from typing import List, NamedTuple, TypeVar, Type, Dict, Any, Set, Tuple

# Top level configuration keys
LEGACY_CONFIG_KEYS = {"args", "dirs", "env", "exit_code", "stderr", "stdout"}
CONFIG_KEYS = {"operations", "proposals"}


# Supported operations
SUPPORTED_OPERATIONS = {"run", "wait", "read", "write", "connect", "send", "recv"}


class WasiVersion(StrEnum):
    WASM32_WASIP1 = 'wasm32-wasip1'
    WASM32_WASIP2 = 'wasm32-wasip2'
    WASM32_WASIP3 = 'wasm32-wasip3'


F = TypeVar("F", bound="Failure")


class Failure(NamedTuple):
    type: str
    message: str

    @classmethod
    def expectation(cls, message: str) -> "Failure":
        return Failure(type="Expectation mismatch", message=message)

    @classmethod
    def unexpected(cls, message: str) -> "Failure":
        return Failure(type="Unexpected", message=message)


class Result(NamedTuple):
    is_executed: bool
    failures: List[Failure]

    @property
    def failed(self) -> bool:
        return len(self.failures) > 0


class ProtocolType(StrEnum):
    TCP = 'tcp'
    UDP = 'udp'
    HTTP = 'http'


R = TypeVar("R", bound="Run")


class Run(NamedTuple):
    args: List[str] = []
    env: Dict[str, str] = {}
    dirs: List[Tuple[Path, str]] = []

    @classmethod
    def from_config(cls: Type[R], test_config_path: Path, config: Dict[str, Any]) -> R:
        default = cls()
        dirs = config.get("dirs", default.dirs)
        dir_pairs = [(test_config_path.parent / d, d) for d in dirs]
        return cls(
            args=config.get("args", default.args),
            env=config.get("env", default.env),
            dirs=dir_pairs
        )


W = TypeVar("W", bound="Wait")


class Wait(NamedTuple):
    exit_code: int = 0

    @classmethod
    def from_config(cls: Type[W], config: Dict[str, Any]) -> W:
        default = cls()
        return cls(
            exit_code=config.get("exit_code", default.exit_code)
        )


S = TypeVar("S", bound="Send")


class Send(NamedTuple):
    id: str
    payload: str

    @classmethod
    def from_config(cls: Type[S], config: Dict[str, Any]) -> S:
        if "id" not in config:
            raise ValueError("Send operation requires 'id' field")
        return cls(
            id=config["id"],
            payload=config.get("payload", "")
        )


Rv = TypeVar("Rv", bound="Recv")


class Recv(NamedTuple):
    id: str
    payload: str

    @classmethod
    def from_config(cls: Type[Rv], config: Dict[str, Any]) -> Rv:
        if "id" not in config:
            raise ValueError("Recv operation requires 'id' field")
        return cls(
            id=config["id"],
            payload=config.get("payload", "")
        )


Rx = TypeVar("Rx", bound="Read")


class Read(NamedTuple):
    id: str = "stdout"
    payload: str = ""

    @classmethod
    def from_config(cls: Type[Rx], config: Dict[str, Any]) -> Rx:
        default = cls()
        return cls(
            id=config.get("id", default.id),
            payload=config.get("payload", default.payload)
        )


Wr = TypeVar("Wr", bound="Write")


class Write(NamedTuple):
    id: str = "write"
    payload: str = ""

    @classmethod
    def from_config(cls: Type[Wr], config: Dict[str, Any]) -> Wr:
        default = cls()
        return cls(
            id=config.get("id", default.id),
            payload=config.get("payload", default.payload)
        )


C = TypeVar("C", bound="Connect")


class Connect(NamedTuple):
    id: str = "server"
    protocol_type: ProtocolType = ProtocolType("tcp")

    @classmethod
    def from_config(cls: Type[C], config: Dict[str, Any]) -> C:
        default = cls()
        return cls(
            id=config.get("id", default.id),
            protocol_type=ProtocolType(config.get("protocol_type", default.protocol_type))
        )


Operation = Run | Wait | Read | Write | Connect | Send | Recv


class WasiProposal(StrEnum):
    HTTP = 'http'
    SOCKETS = 'sockets'


T = TypeVar("T", bound="Config")


class Config(NamedTuple):
    # List of operations.
    operations: List[Operation] = [Run(), Wait()]
    # WASI proposals needed for the test.
    proposals: List[WasiProposal] = []

    @classmethod
    def from_file(cls: Type[T], config_file: str) -> T:
        with open(config_file, encoding="utf-8") as file:
            dict_config = json.load(file)

        test_config_path = Path(config_file)
        if dict_config.get("operations") is not None or dict_config.get("proposals") is not None:
            cls._validate_config(dict_config, CONFIG_KEYS)

            operations = []
            if dict_config.get("operations") is not None:
                operations = cls._operations_from_config(test_config_path, dict_config.get("operations"))

            proposals = []
            if dict_config.get("proposals") is not None:
                proposals = cls._proposals_from_config(dict_config.get("proposals"))

            return cls(operations=operations, proposals=proposals)

        cls._validate_config(dict_config, LEGACY_CONFIG_KEYS)

        # Construct the configuration from the v0 configuration.
        # The legacy configuration can be described in terms of
        # `Run`, `Read` and `Wait` operations.
        run_op = Run.from_config(
            test_config_path,
            dict_config,
        )

        legacy_operations: List[Operation] = [run_op]

        if dict_config.get("stdout") is not None:
            legacy_operations.append(Read(id="stdout", payload=dict_config.get("stdout")))

        if dict_config.get("stderr") is not None:
            legacy_operations.append(Read(id="stderr", payload=dict_config.get("stderr")))

        wait_op = Wait(
            exit_code=dict_config.get("exit_code", 0)
        )
        legacy_operations.append(wait_op)

        return cls(
            operations=legacy_operations,
            # Tests which require explicit proposals must be
            # configured using the new configuration.
            # See http-response.json
            # We could potentially use additional heuristics to derive
            # the proposals to enable, but that doesn't seem entirely
            # reliable, plus we'd be introducing a third level of
            # configuration.
            proposals=[],
        )

    def args_env_dirs(self) -> Tuple[List[str], Dict[str, str], List[Tuple[Path, str]]]:
        for op in self.operations:
            match op:
                case Run(args, env, dirs):
                    return (args, env, dirs)
        return ([], {}, [])

    def proposals_as_str(self) -> List[str]:
        return [p.value for p in self.proposals]

    @classmethod
    def _validate_config(cls: Type[T], dict_config: Dict[str, Any], expected_keys: Set[str]) -> None:
        # Check that the test configuration is unique, either v0 or v1
        actual_keys = set(dict_config.keys())
        if (actual_keys & CONFIG_KEYS) and (actual_keys & LEGACY_CONFIG_KEYS):
            raise ValueError("Cannot mix configuration styles")

        # Warn if there are any extra unknown fields in the configuration, relative to
        # the expected keys.
        for field_name in dict_config:
            if field_name not in expected_keys:
                logging.warning("Unknown field in the config file: %s", field_name)

    @classmethod
    def _operations_from_config(cls: Type[T], test_config_path: Path, ops: List[Any]) -> List[Operation]:
        operations: List[Operation] = []
        for op in ops:
            ty = op.get("type")
            if ty is None or ty not in SUPPORTED_OPERATIONS:
                raise ValueError(f"Unsupported operation type {ty}")

            match ty:
                case "run":
                    operations.append(Run.from_config(test_config_path, op))
                case "wait":
                    operations.append(Wait.from_config(op))
                case "read":
                    operations.append(Read.from_config(op))
                case "write":
                    operations.append(Write.from_config(op))
                case "connect":
                    operations.append(Connect.from_config(op))
                case "send":
                    operations.append(Send.from_config(op))
                case "recv":
                    operations.append(Recv.from_config(op))

        return operations

    @classmethod
    def _proposals_from_config(cls: Type[T], proposals: List[Any]) -> List[WasiProposal]:
        return [WasiProposal(p) for p in proposals]


class TestCase(NamedTuple):
    name: str
    argv: List[str]
    config: Config
    result: Result
    duration_s: float


class TestCaseRunnerBase:
    config: Config
    _failures: List[Failure]

    def __init__(self, config: Config) -> None:
        self.config = config
        self._failures = []

    def do_run(self, run: Run) -> None:
        raise NotImplementedError()

    def do_write(self, write: Write) -> None:
        raise NotImplementedError()

    def do_read(self, read: Read) -> None:
        raise NotImplementedError()

    def do_wait(self, wait: Wait) -> None:
        raise NotImplementedError()

    def do_connect(self, conn: Connect) -> None:
        raise NotImplementedError()

    def do_send(self, send: Send) -> None:
        raise NotImplementedError()

    def do_recv(self, recv: Recv) -> None:
        raise NotImplementedError()

    def do_cleanup(self, successful: bool) -> None:
        raise NotImplementedError()

    def as_result(self) -> Result:
        failures, self._failures = self._failures, []
        return Result(is_executed=True, failures=failures)

    def has_failure(self) -> bool:
        return bool(self._failures)

    def run(self) -> Result:
        successful = False
        try:
            for op in self.config.operations:
                if self.has_failure():
                    break

                # The isinstance asserts in these clauses might seem
                # redudant, given the match.  Asserts merely exist to
                # ensure that mypy can fully resolve the underlying
                # type; else it will report errors like:
                #   wasi_test_runner/runtime_adapter.py:131: error: Argument 2 to "_handle_read"
                #   has incompatible type "Read"; expected "Read" [arg-type]
                match op:
                    case Run() as run:
                        assert isinstance(run, Run)
                        self.do_run(run)
                    case Write() as write:
                        assert isinstance(write, Write)
                        self.do_write(write)
                    case Read() as read:
                        assert isinstance(read, Read)
                        self.do_read(read)
                    case Wait() as wait:
                        assert isinstance(wait, Wait)
                        self.do_wait(wait)
                    case Connect() as conn:
                        assert isinstance(conn, Connect)
                        self.do_connect(conn)
                    case Send() as send:
                        assert isinstance(send, Send)
                        self.do_send(send)
                    case Recv() as recv:
                        assert isinstance(recv, Recv)
                        self.do_recv(recv)

            successful = not self.has_failure()
        finally:
            self.do_cleanup(successful)

        return self.as_result()


class TestCaseValidator(TestCaseRunnerBase):
    _config_path: str
    _has_proc: bool
    _streams: Set[str]

    def __init__(self, config: Config, config_path: str) -> None:
        TestCaseRunnerBase.__init__(self, config)
        self._config_path = config_path
        self._has_proc = False
        self._streams = set()

    def assert_proc(self, op: Any) -> None:
        assert self._has_proc, f"{op}: no process running"

    def assert_no_proc(self, op: Any) -> None:
        assert not self._has_proc, f"{op}: process still running"

    def assert_stream(self, op: Any, name: str) -> None:
        assert name in self._streams, f"{op}: no such stream: {name}"

    def assert_no_stream(self, op: Any, name: str) -> None:
        assert name not in self._streams, f"{op}: stream exists: {name}"

    def do_run(self, run: Run) -> None:
        self.assert_no_proc(run)
        self._has_proc = True

    def do_write(self, write: Write) -> None:
        self.assert_proc(write)
        match write.id:
            case "stdin": pass
            case name: self.assert_stream(write, name)

    def do_read(self, read: Read) -> None:
        self.assert_proc(read)
        match read.id:
            case "stdout": pass
            case "stderr": pass
            case name: self.assert_stream(read, name)

    def do_wait(self, wait: Wait) -> None:
        self.assert_proc(wait)
        self._has_proc = False
        self._streams.clear()

    def do_connect(self, conn: Connect) -> None:
        self.assert_proc(conn)
        self.assert_no_stream(conn, conn.id)
        assert conn.protocol_type == ProtocolType.TCP, \
            f"{conn}: {conn.protocol_type} not supported"
        self._streams.add(conn.id)

    def do_send(self, send: Send) -> None:
        self.assert_proc(send)
        self.assert_stream(send, send.id)

    def do_recv(self, recv: Recv) -> None:
        self.assert_proc(recv)
        self.assert_stream(recv, recv.id)

    def do_cleanup(self, successful: bool) -> None:
        if successful:
            self.assert_no_proc(self._config_path)
            assert not bool(self._streams)

    def validate(self) -> None:
        self.run()
