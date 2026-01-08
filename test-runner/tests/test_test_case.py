from json import JSONDecodeError
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

import pytest

from wasi_test_runner.test_case import (
    Config, Failure, Result, Run, Wait, Read, Connect, Send, Recv, ProtocolType
)


@patch("builtins.open", new_callable=mock_open, read_data="{}")
def test_test_config_sholud_load_defaults_for_empty_json(_mock_file: Mock) -> None:
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
def test_test_config_sholud_load_values_from_json(_mock_file: Mock) -> None:
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
def test_test_config_sholud_fail_when_invalid_json(_mock_file: Mock) -> None:
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
    results = Result([], True, [Failure("type", "message")])

    assert results.failed is True


def test_test_results_should_not_mark_failed_if_no_failure() -> None:
    results = Result([], True, [])

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
