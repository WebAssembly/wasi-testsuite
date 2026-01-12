import importlib.util
import subprocess
import sys
import shutil
import socket
from pathlib import Path
from typing import NamedTuple, List, Tuple, Any

from .test_case import Result, WasiVersion, Config, Run, Read, Wait, Send, Recv, Failure, Connect, ProtocolType


class RuntimeMeta(NamedTuple):
    name: str
    version: str
    supported_wasi_versions: frozenset[WasiVersion]

    def __str__(self) -> str:
        return f"{self.name} {self.version}"


class RuntimeAdapterError(Exception):
    adapter_path: str

    def __init__(self, adapter_path: str) -> None:
        self.adapter_path = adapter_path


class LegacyRuntimeAdapterError(RuntimeAdapterError):
    adapter_path: str


class UnavailableRuntimeAdapterError(RuntimeAdapterError):
    error: Exception

    def __init__(self, adapter_path: str, error: Exception) -> None:
        RuntimeAdapterError.__init__(self, adapter_path)
        self.error = error


def _assert_not_legacy_adapter(adapter_path: str) -> None:
    """
    Raise an exception if the python file at ADAPTER_PATH isn't
    loadable as a normal Python module.
    """
    argv = [sys.executable, adapter_path, "--version"]
    try:
        result = subprocess.run(argv, encoding="UTF-8", check=True,
                                capture_output=True)
    except subprocess.CalledProcessError as e:
        if 'FileNotFoundError' in e.stderr:
            # The adapter is valid Python.  Running it tries to spawn
            # the engine subprocess, but couldn't find the binary.  This
            # indicates a legacy adapter.py.
            raise LegacyRuntimeAdapterError(adapter_path) from e
        # Some other error running adapter.py; could be a legacy
        # adapter, could just be a typo.  Propagate the error.
        raise UnavailableRuntimeAdapterError(adapter_path, e) from e
    assert result.stderr == "", result.stderr
    if result.stdout:
        # Running the adapter as a subprocess succeeded and produced
        # --version output: the engine is available but the adapter is
        # legacy.
        raise LegacyRuntimeAdapterError(adapter_path)
    # Otherwise if loading the file produces no output, then we assume
    # it's a module and not legacy.


def _load_adapter_as_module(adapter_path: str) -> Any:
    path = Path(adapter_path)
    spec = importlib.util.spec_from_file_location(path.name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RuntimeAdapter:
    def __init__(self, adapter_path: str) -> None:
        _assert_not_legacy_adapter(adapter_path)
        self._adapter = _load_adapter_as_module(adapter_path)
        try:
            name = self._adapter.get_name()
            version = self._adapter.get_version()
            wasi_versions = frozenset(
                WasiVersion(v) for v in self._adapter.get_wasi_versions()
            )
        except subprocess.CalledProcessError as e:
            raise UnavailableRuntimeAdapterError(adapter_path, e) from e
        except FileNotFoundError as e:
            raise UnavailableRuntimeAdapterError(adapter_path, e) from e
        self._meta = RuntimeMeta(name, version, wasi_versions)

    def get_meta(self) -> RuntimeMeta:
        return self._meta

    def compute_argv(self, test_path: str,
                     config: Config,
                     wasi_version: WasiVersion) -> List[str]:
        # too-many-positional-arguments is a post-3.0 pylint message.
        # pylint: disable-msg=unknown-option-value
        # pylint: disable-msg=too-many-arguments
        # pylint: disable-msg=too-many-positional-arguments
        argv = self._adapter.compute_argv(test_path=test_path,
                                          config=config,
                                          wasi_version=wasi_version.value)
        assert isinstance(argv, list)
        assert all(isinstance(arg, str) for arg in argv)
        return argv

    def run_test(self, test_path: str, config: Config, wasi_version: WasiVersion) -> Result:
        # pylint: disable=too-many-branches
        argv = self.compute_argv(test_path, config, wasi_version)
        result = Result(argv=argv, is_executed=True, failures=[])

        proc: subprocess.Popen[Any] | None = None
        cleanup_dirs = None
        try:
            for op in config.operations:
                match op:
                    case Run(_, _, dirs):
                        _cleanup_test_output(dirs)
                        # pylint: disable=consider-using-with
                        proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        cleanup_dirs = dirs
                    case Read() as read:
                        if proc is None:
                            result.failures.append(Failure.unexpected("Read operation called before Run"))
                        else:
                            # Instance asserts might seems redudant here, given the match.
                            # Asserts merely exist to ensure that mypy can fully resolve the underlying type;
                            # else it will report errors like:
                            #   wasi_test_runner/runtime_adapter.py:131: error: Argument 2 to "_handle_read" has incompatible type "Read"; expected "Read"  [arg-type]
                            assert isinstance(read, Read)
                            _handle_read(proc, read, result)
                    case Wait() as wait:
                        if proc is None:
                            result.failures.append(Failure.unexpected("Wait operation called before Run"))
                        else:
                            assert isinstance(wait, Wait)
                            _handle_wait(proc, wait, result)
                    case Connect() as conn:
                        if proc is None:
                            result.failures.append(Failure.unexpected("Connect operation called before Run"))
                        else:
                            assert isinstance(conn, Connect)
                            _handle_connect(proc, config, conn, result)
                    case Send() as send:
                        assert isinstance(send, Send)
                        _handle_send(config, send, result)
                    case Recv() as recv:
                        assert isinstance(recv, Recv)
                        _handle_recv(config, recv, result)
                    case _:
                        pass

        finally:
            if cleanup_dirs:
                _cleanup_test_output(cleanup_dirs)
            # If we finalized processing all the operations, ensure
            # the the subprocess is correctly terminated.
            if proc:
                try:
                    _, _ = proc.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    result.failures.append(Failure.unexpected("Process timed out"))

        return result


def _handle_read(proc: subprocess.Popen[Any], spec: Read, result: Result) -> None:
    if spec.id == "stdout":
        if proc.stdout is None:
            result.failures.append(Failure.unexpected(f"{spec.id} is not available"))
            return
        payload = proc.stdout.readline().strip()
        if payload != spec.payload:
            result.failures.append(Failure.expectation(f"{spec.id} failed: expected {spec.payload}, got {payload}"))

    if spec.id == "stderr":
        if proc.stderr is None:
            result.failures.append(Failure.unexpected(f"{spec.id} is not available"))
            return
        payload = proc.stderr.readline().strip()
        if payload != spec.payload:
            result.failures.append(Failure.expectation(f"{spec.id} failed: expected {spec.payload}, got {payload}"))


def _handle_wait(proc: subprocess.Popen[Any], spec: Wait, result: Result) -> None:
    try:
        out, err = proc.communicate(timeout=5)
        if spec.exit_code != proc.returncode:
            msg = f"{spec} failed: expected {spec.exit_code}, got {proc.returncode}"

            if out:
                msg += f"\n\n==STDOUT==\n{out}"

            if err:
                msg += f"\n\n==STDERR==\n{err}"

            result.failures.append(Failure.expectation(msg))

    except subprocess.TimeoutExpired:
        result.failures.append(Failure.expectation(f"{spec} failed: timeout expired"))


def _handle_connect(proc: subprocess.Popen[Any], config: Config, spec: Connect, result: Result) -> None:
    if spec.protocol_type != ProtocolType.TCP:
        raise RuntimeError(f"Unimplemented support for protocol {spec.protocol_type}")
    # Server not running, something's wrong.
    if proc.poll() is not None:
        _, err = proc.communicate()
        result.failures.append(Failure.unexpected(f"{spec}: Could not connect to server {err}"))
        return

    # In the connect case, we need to discover the port.
    # If there's no stdout, add a failure.
    if proc.stdout is None:
        result.failures.append(Failure.unexpected(f"{spec}: No connection information available"))
        return

    host, port = proc.stdout.readline().strip().split(':')
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, int(port)))
        config.connections[spec.id] = sock
    except socket.timeout:
        host_port = host + ":" + port
        result.failures.append(Failure.unexpected(f"{spec}: Could not connect to {host_port}"))


def _handle_send(config: Config, spec: Send, result: Result) -> None:
    if config.connections[spec.id] is None:
        result.failures.append(Failure.unexpected(f"{spec}: No connection declared for id {spec.id}"))
        return

    sock = config.connections[spec.id]
    sock.sendall(spec.payload.encode('utf-8'))


def _handle_recv(config: Config, spec: Recv, result: Result) -> None:
    if config.connections[spec.id] is None:
        result.failures.append(Failure.unexpected(f"{spec}: No connection declared for id {spec.id}"))
        return

    sock = config.connections[spec.id]
    response_bytes = sock.recv(len(spec.payload))
    response = response_bytes.decode('utf-8')
    if response != spec.payload:
        result.failures.append(Failure.unexpected(f"{spec}: Expected {spec.payload}, got {response}"))


def _cleanup_test_output(dirs: List[Tuple[Path, str]]) -> None:
    for host, _guest in dirs:
        for f in host.glob("**/*.cleanup"):
            if f.is_file():
                f.unlink()
            elif f.is_dir():
                shutil.rmtree(f)
