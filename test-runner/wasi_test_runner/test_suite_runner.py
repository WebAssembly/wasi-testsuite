import glob
import json
import os
import re
import shutil
import subprocess
import socket
import time

from datetime import datetime
from pathlib import Path
from typing import List, NamedTuple, Tuple, Dict, Any, IO

import requests

from .filters import TestFilter
from .runtime_adapter import RuntimeAdapter
from .test_case import (
    Result, Failure, WasiVersion, Config,
    TestCase, TestCaseRunnerBase, TestCaseValidator,
    # Operation types
    Run, Read, Write, Wait, Send, Recv, Connect, Request, Kill
)
from .reporters import TestReporter
from .test_suite import TestSuite, TestSuiteMeta


class Manifest(NamedTuple):
    name: str
    wasi_version: WasiVersion


class TestCaseRunner(TestCaseRunnerBase):
    # pylint: disable-msg=too-many-instance-attributes
    _test_path: str
    _wasi_version: WasiVersion
    _runtime: RuntimeAdapter
    _proc: subprocess.Popen[Any] | None
    _cleanup_dirs: List[Path]
    _pipes: Dict[str, IO[str]]
    _sockets: Dict[str, socket.socket]
    _last_argv: List[str]
    _http_server: str | None

    def __init__(self, config: Config, test_path: str, wasi_version: WasiVersion,
                 runtime: RuntimeAdapter) -> None:
        TestCaseRunnerBase.__init__(self, config)
        self._test_path = test_path
        self._wasi_version = wasi_version
        self._runtime = runtime
        self._proc = None
        self._cleanup_dirs = []
        self._pipes = {}
        self._sockets = {}
        self._last_argv = []
        self._http_server = None

    def _add_cleanup_dir(self, d: Path) -> None:
        _cleanup_test_output(d)
        self._cleanup_dirs.append(d)

    def _wait(self, timeout: float | None) -> Tuple[int, str, str]:
        proc = self._proc
        assert proc is not None
        out, err = proc.communicate(timeout=timeout)
        self._proc = None
        return proc.returncode, out, err

    def fail_unexpected(self, msg: str) -> None:
        self._failures.append(Failure.unexpected(msg))

    def fail_expectation(self, msg: str) -> None:
        self._failures.append(Failure.expectation(msg))

    def has_failure(self) -> bool:
        return bool(self._failures)

    def add_socket(self, name: str, sock: socket.socket) -> None:
        self._sockets[name] = sock

    def add_pipe(self, name: str, pipe: IO[str]) -> None:
        self._pipes[name] = pipe

    def get_socket(self, name: str) -> socket.socket:
        assert name in self._sockets
        return self._sockets[name]

    def get_pipe(self, name: str) -> IO[str]:
        assert name in self._pipes
        return self._pipes[name]

    def last_argv(self) -> List[str]:
        return self._last_argv

    def get_http_server(self) -> str | None:
        if self._http_server:
            return self._http_server
        line = self.get_pipe('stderr').readline().strip()
        start = line.find('http://')
        if start < 0:
            self.fail_unexpected(f"Expected 'http://' in first line, got {line}")  # noqa: E231
            return None
        # The server URL starts with http:// and ends at EOL or whitespace.
        self._http_server = line[start:].split()[0]
        return self._http_server

    def do_run(self, run: Run) -> None:
        for (host, _guest) in run.dirs:
            self._add_cleanup_dir(host)
        proposals = self.config.proposals_as_str()
        argv = self._runtime.compute_argv(
            self._test_path, run.args, run.env, run.dirs, proposals,
            self._wasi_version)
        self._last_argv = argv
        try:
            # pylint: disable-msg=consider-using-with
            self._proc = subprocess.Popen(
                argv,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdin, stdout, stderr = \
                self._proc.stdin, self._proc.stdout, self._proc.stderr
            assert stdin is not None
            assert stdout is not None
            assert stderr is not None
            self.add_pipe('stdin', stdin)
            self.add_pipe('stdout', stdout)
            self.add_pipe('stderr', stderr)
        except (OSError, ValueError) as e:
            self.fail_unexpected(f"Failed to start process: {e}")

    def do_read(self, read: Read) -> None:
        stream = self.get_pipe(read.id)
        expected_length = len(read.payload)
        payload = stream.read(expected_length)
        if payload != read.payload:
            self.fail_expectation(f"{read} {read.id} failed: expected {read.payload}, got {payload}")

    def do_write(self, write: Write) -> None:
        stream = self.get_pipe(write.id)
        stream.write(write.payload)
        stream.flush()

    def do_wait(self, wait: Wait) -> None:
        try:
            exit_code, out, err = self._wait(5)
            if wait.exit_code != exit_code:
                msg = f"{wait} failed: expected {wait.exit_code}, got {exit_code}"
                msg = _append_stdout_and_stderr(msg, out, err)
                self.fail_expectation(msg)

        except subprocess.TimeoutExpired:
            self.fail_expectation(f"{wait} failed: timeout expired")

    def do_connect(self, conn: Connect) -> None:
        # Discover the port.
        line = self.get_pipe('stdout').readline().strip()
        match line.split(':'):
            case [host, port_str] if port_str.isnumeric():
                port = int(port_str)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sock.connect((host, port))
                    self.add_socket(conn.id, sock)
                except (socket.timeout, ConnectionRefusedError, OSError) as e:
                    sock.close()
                    self.fail_unexpected(
                        f"{conn}: Could not connect to {host}:{port}: {e}")  # noqa: E231
                    return
            case _:
                self.fail_unexpected(
                    f"{conn}: Expected address information to be available as <host>: <port>, found {line}")
                return

    def do_send(self, send: Send) -> None:
        sock = self.get_socket(send.id)
        try:
            sock.sendall(send.payload.encode('utf-8'))
        except (OSError, socket.error) as e:
            self.fail_unexpected(f"{send}: Failed to send data: {e}")

    def do_recv(self, recv: Recv) -> None:
        sock = self.get_socket(recv.id)
        try:
            response_bytes = sock.recv(len(recv.payload))
            response = response_bytes.decode('utf-8')
            if response != recv.payload:
                self.fail_unexpected(f"{recv}: Expected {recv.payload}, got {response}")
        except (OSError, socket.error) as e:
            self.fail_unexpected(f"{recv}: Failed to receive data: {e}")
        except UnicodeDecodeError as e:
            self.fail_unexpected(f"{recv}: Failed to decode response: {e}")

    def do_request(self, req: Request) -> None:
        # pylint: disable-msg=too-many-return-statements
        http_server = self.get_http_server()
        if http_server is None:
            return
        url = http_server + req.path
        try:
            response = requests.request(req.method, url, timeout=5)
        except requests.exceptions.Timeout:
            self.fail_unexpected(f"{req}: Timeout waiting for response")
            return
        except requests.exceptions.RequestException as e:
            self.fail_unexpected(f"{req}: Failed to make request: {e}")
            return
        if response.status_code != req.response.status:
            self.fail_unexpected(
                f"{req}: Expected status {req.response.status}, got {response.status_code}")
            return
        for h, expected in req.response.headers.items():
            if h not in response.headers:
                self.fail_unexpected(f"{req}: Response missing header {h}")
                return
            actual = response.headers[h]
            if actual != expected:
                self.fail_unexpected(
                    f"{req}: Expected response header {h}={expected}, got {actual}")
                return
        if response.text != req.response.body:
            self.fail_unexpected(
                f"{req}: Expected response body '{req.response.body}', got '{response.text}'")
            return

    def do_kill(self, kill: Kill) -> None:
        try:
            proc = self._proc
            assert proc is not None
            proc.send_signal(kill.signal)
        except OSError as e:
            self.fail_unexpected(f"{kill}: Failed to send {kill.signal}: {e}")

    def do_cleanup(self, successful: bool) -> None:
        if self._proc:
            self._proc.kill()
            try:
                _, out, err = self._wait(timeout=5)
                self.fail_unexpected(
                    _append_stdout_and_stderr("", out, err))
            except subprocess.TimeoutExpired:
                self.fail_unexpected(
                    f"Timeout expired after killing proc {self._proc}")
                self._proc = None

        for d in self._cleanup_dirs:
            _cleanup_test_output(d)
        self._cleanup_dirs = []


# pylint: disable-msg=too-many-locals
def run_tests_from_test_suite(
    test_suite_path: str,
    runtime: RuntimeAdapter,
    reporters: List[TestReporter],
    filters: List[TestFilter]
) -> TestSuite:
    test_cases: List[TestCase] = []
    test_start = datetime.now()

    manifest = _read_manifest(Path(test_suite_path))
    meta = TestSuiteMeta(manifest.name, manifest.wasi_version,
                         runtime.get_meta())

    for test_path in glob.glob(os.path.join(test_suite_path, "*.wasm")):
        test_name = os.path.splitext(os.path.basename(test_path))[0]
        for filt in filters:
            # for now, just drop the skip reason string. it might be
            # useful to make reporters report it.
            skip, _ = filt.should_skip(meta, test_name)
            if skip:
                test_case = _skip_single_test(test_path)
                break
        else:
            test_case = _execute_single_test(runtime, meta, test_path)
        test_cases.append(test_case)
        for reporter in reporters:
            reporter.report_test(meta, test_case)

    elapsed = (datetime.now() - test_start).total_seconds()

    return TestSuite(
        meta=meta,
        time=test_start,
        duration_s=elapsed,
        test_cases=test_cases,
    )


def _skip_single_test(test_path: str) -> TestCase:
    config = _read_test_config(test_path)
    return TestCase(
        name=os.path.splitext(os.path.basename(test_path))[0],
        argv=[],
        config=config,
        result=Result(is_executed=False, failures=[]),
        duration_s=0,
    )


def _append_stdout_and_stderr(msg: str, out: str | None, err: str | None) -> str:
    if out:
        msg += f"\n\n==STDOUT==\n{out}"

    if err:
        msg += f"\n\n==STDERR==\n{err}"

    return msg


def _cleanup_test_output(host_dir: Path) -> None:
    for f in host_dir.glob("**/*.cleanup"):
        if f.is_file():
            f.unlink()
        elif f.is_dir():
            shutil.rmtree(f)


def _execute_single_test(
    runtime: RuntimeAdapter, meta: TestSuiteMeta, test_path: str
) -> TestCase:
    config = _read_test_config(test_path)
    runner = TestCaseRunner(config, test_path, meta.wasi_version, runtime)
    test_start = time.time()
    result = runner.run()
    elapsed = time.time() - test_start

    return TestCase(
        name=os.path.splitext(os.path.basename(test_path))[0],
        argv=runner.last_argv(),
        config=config,
        result=result,
        duration_s=elapsed,
    )


def _read_test_config(test_path: str) -> Config:
    config_file = re.sub("\\.wasm$", ".json", test_path)
    if os.path.exists(config_file):
        config = Config.from_file(config_file)
        TestCaseValidator(config, config_file).validate()
        return config
    return Config()


def _read_manifest(test_suite_path: Path) -> Manifest:
    manifest_path = test_suite_path / "manifest.json"
    if test_suite_path.name in WasiVersion:
        name = str(test_suite_path.parent)
        wasi_version = WasiVersion(test_suite_path.name)
    else:
        name = str(test_suite_path)
        wasi_version = WasiVersion.WASM32_WASIP1

    if manifest_path.exists():
        with open(str(manifest_path), encoding="utf-8") as file:
            contents = json.load(file)
            assert isinstance(contents, dict)
            for k, v in contents.items():
                match k:
                    case "name":
                        assert isinstance(v, str)
                        name = v
                    case "version":
                        assert v in WasiVersion
                        wasi_version = WasiVersion[v]
                    case _:
                        raise RuntimeError(f"unexpected manifest option: {k}={v}")

    return Manifest(name=name, wasi_version=wasi_version)
