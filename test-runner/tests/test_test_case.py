from json import JSONDecodeError
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

import pytest

from wasi_test_runner.test_case import (
    Config, Failure, Result, Run, Wait, Read, Write, Connect, Send, Recv,
    ProtocolType, WasiProposal, TestCaseValidator
)


@patch("builtins.open", new_callable=mock_open, read_data="{}")
def test_test_config_should_load_defaults_for_empty_json(_mock_file: Mock) -> None:
    config = Config.from_file("file")

    assert len(config.operations) == 2
    run = config.operations[0]
    assert isinstance(run, Run)
    assert run.args == []
    assert run.dirs == []
    assert run.env == {}

    wait = config.operations[1]
    assert isinstance(wait, Wait)
    assert wait.exit_code == 0


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"args": ["a", "b"], "exit_code": 5}',
)
def test_test_config_should_load_values_from_json(_mock_file: Mock) -> None:
    config = Config.from_file("file")

    assert len(config.operations) == 2
    run = config.operations[0]
    assert isinstance(run, Run)
    assert run.args == ["a", "b"]
    assert run.dirs == []
    assert run.env == {}

    wait = config.operations[1]
    assert isinstance(wait, Wait)
    assert wait.exit_code == 5


@patch("builtins.open", new_callable=mock_open, read_data="not-json")
def test_test_config_should_fail_when_invalid_json(_mock_file: Mock) -> None:
    with pytest.raises(JSONDecodeError):
        Config.from_file("file")


@patch("builtins.open", new_callable=mock_open, read_data='{"invalid-field": 1}')
def test_test_config_should_warn_when_unknown_field(_mock_file: Mock) -> None:
    with patch("logging.warning") as mocked_logger:
        Config.from_file("file")
        mocked_logger.assert_called_once()


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"operations": [{"type": "run"}], "args": ["a"]}',
)
def test_test_config_should_fail_when_mixing_config_styles(_mock_file: Mock) -> None:
    with pytest.raises(ValueError, match="Cannot mix configuration styles"):
        Config.from_file("file")


def test_test_results_should_mark_failed_if_multiple_failures() -> None:
    results = Result(True, [Failure("type", "message")])

    assert results.failed is True


def test_test_results_should_not_mark_failed_if_no_failure() -> None:
    results = Result(True, [])

    assert results.failed is False


def test_run_from_config_with_defaults() -> None:
    run = Run.from_config(Path("/test/path"), {})

    assert run.args == []
    assert run.env == {}
    assert run.dirs == []


def test_run_from_config_with_values() -> None:
    config = {
        "args": ["arg1", "arg2"],
        "env": {"KEY": "value"},
        "dirs": [".", "subdir"]
    }
    run = Run.from_config(Path("/test/path"), config)

    assert run.args == ["arg1", "arg2"]
    assert run.env == {"KEY": "value"}
    assert len(run.dirs) == 2
    assert all(isinstance(d, tuple) and len(d) == 2 for d in run.dirs)
    assert all(isinstance(d[0], Path) and isinstance(d[1], str) for d in run.dirs)


def test_wait_from_config_with_defaults() -> None:
    wait = Wait.from_config({})

    assert wait.exit_code == 0


def test_wait_from_config_with_value() -> None:
    wait = Wait.from_config({"exit_code": 42})

    assert wait.exit_code == 42


def test_read_from_config_with_defaults() -> None:
    read = Read.from_config({})

    assert read.id == "stdout"
    assert read.payload == ""


def test_read_from_config_with_values() -> None:
    read = Read.from_config({"id": "stderr", "payload": "error message"})

    assert read.id == "stderr"
    assert read.payload == "error message"


def test_write_from_config_with_defaults() -> None:
    write = Write.from_config({})

    assert write.id == "write"
    assert write.payload == ""


def test_write_from_config_with_values() -> None:
    write = Write.from_config({"id": "stdin", "payload": "input data"})

    assert write.id == "stdin"
    assert write.payload == "input data"


def test_connect_from_config_with_defaults() -> None:
    connect = Connect.from_config({})

    assert connect.id == "server"
    assert connect.protocol_type == ProtocolType.TCP


def test_connect_from_config_with_values() -> None:
    connect = Connect.from_config({"id": "custom", "protocol_type": "udp"})

    assert connect.id == "custom"
    assert connect.protocol_type == ProtocolType.UDP


def test_send_from_config_requires_id() -> None:
    with pytest.raises(ValueError, match="Send operation requires 'id' field"):
        Send.from_config({})


def test_send_from_config_with_values() -> None:
    send = Send.from_config({"id": "conn1", "payload": "hello"})

    assert send.id == "conn1"
    assert send.payload == "hello"


def test_send_from_config_with_default_payload() -> None:
    send = Send.from_config({"id": "conn1"})

    assert send.id == "conn1"
    assert send.payload == ""


def test_recv_from_config_requires_id() -> None:
    with pytest.raises(ValueError, match="Recv operation requires 'id' field"):
        Recv.from_config({})


def test_recv_from_config_with_values() -> None:
    recv = Recv.from_config({"id": "conn1", "payload": "world"})

    assert recv.id == "conn1"
    assert recv.payload == "world"


def test_recv_from_config_with_default_payload() -> None:
    recv = Recv.from_config({"id": "conn1"})

    assert recv.id == "conn1"
    assert recv.payload == ""


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"operations": [{"type": "run"}, {"type": "wait"}], "proposals": []}',
)
def test_new_config_with_empty_proposals(_mock_file: Mock) -> None:
    config = Config.from_file("file")

    assert len(config.proposals) == 0


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"operations": [{"type": "run"}], "proposals": ["http", "sockets"]}',
)
def test_new_config_with_multiple_proposals(_mock_file: Mock) -> None:
    config = Config.from_file("file")

    assert len(config.proposals) == 2
    assert config.proposals[0] == WasiProposal.HTTP
    assert config.proposals[1] == WasiProposal.SOCKETS


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"operations": [{"type": "run"}], "proposals": ["invalid"]}',
)
def test_new_config_should_fail_with_invalid_proposal(_mock_file: Mock) -> None:
    with pytest.raises(ValueError):
        Config.from_file("file")


def validate_config(config: Config) -> None:
    TestCaseValidator(config, 'test-config.json').validate()


def test_dry_run_valid_config_should_not_raise() -> None:
    config = Config(operations=[Run(), Wait()])
    validate_config(config)


def test_dry_run_run_without_wait() -> None:
    config = Config(operations=[Run(), Run()])
    with pytest.raises(AssertionError, match="process still running"):
        validate_config(config)


def test_dry_run_read_before_run() -> None:
    config = Config(operations=[Read()])
    with pytest.raises(AssertionError, match="no process running"):
        validate_config(config)


def test_dry_run_write_before_run() -> None:
    config = Config(operations=[Write()])
    with pytest.raises(AssertionError, match="no process running"):
        validate_config(config)


def test_dry_run_wait_before_run() -> None:
    config = Config(operations=[Wait()])
    with pytest.raises(AssertionError, match="no process running"):
        validate_config(config)


def test_dry_run_connect_before_run() -> None:
    config = Config(operations=[Connect()])
    with pytest.raises(AssertionError, match="no process running"):
        validate_config(config)


def test_dry_run_connect_with_non_tcp_protocol() -> None:
    config = Config(operations=[Run(), Connect(protocol_type=ProtocolType.UDP), Wait()])
    with pytest.raises(AssertionError, match="udp not supported"):
        validate_config(config)


def test_dry_run_connect_with_duplicate_id() -> None:
    config = Config(operations=[
        Run(),
        Connect(id="conn1"),
        Connect(id="conn1"),
        Wait()
    ])
    with pytest.raises(AssertionError, match="stream exists: conn1"):
        validate_config(config)


def test_dry_run_send_before_run() -> None:
    config = Config(operations=[Send(id="conn1", payload="test")])
    with pytest.raises(AssertionError, match="no process running"):
        validate_config(config)


def test_dry_run_send_with_undefined_id() -> None:
    config = Config(operations=[Run(), Send(id="conn1", payload="test"), Wait()])
    with pytest.raises(AssertionError, match="no such stream: conn1"):
        validate_config(config)


def test_dry_run_recv_before_run() -> None:
    config = Config(operations=[Recv(id="conn1", payload="test")])
    with pytest.raises(AssertionError, match="no process running"):
        validate_config(config)


def test_dry_run_multiple_errors() -> None:
    config = Config(operations=[Read(), Wait(), Run(), Run()])
    with pytest.raises(AssertionError) as exc_info:
        validate_config(config)
    error_message = str(exc_info.value)
    assert "no process running" in error_message
