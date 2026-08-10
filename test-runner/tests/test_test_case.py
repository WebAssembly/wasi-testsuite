import signal

from json import JSONDecodeError
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

import pytest

from wasi_test_runner.test_case import (
    Config, Failure, Result,
    Run, Wait, Read, Write, Connect, Send, Recv, Request, Response, Kill,
    Endpoint, EndpointMode, EndpointResponse, Server, ServerKind,
    ProtocolType, WasiProposal, WasiWorld, TestCaseValidator
)


@patch("builtins.open", new_callable=mock_open, read_data="{}")
def test_test_config_should_load_defaults_for_empty_json(_mock_file: Mock) -> None:
    config = Config.from_file("file")

    assert len(config.operations) == 2
    run = config.operations[0]
    assert isinstance(run, Run)
    assert run.args == []
    assert run.root is None
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
    assert run.root is None
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
    assert run.root is None


def test_run_from_config_with_values() -> None:
    config = {
        "args": ["arg1", "arg2"],
        "env": {"KEY": "value"},
        "root": "workdir"
    }
    run = Run.from_config(Path("/test/path"), config)

    assert run.args == ["arg1", "arg2"]
    assert run.env == {"KEY": "value"}
    assert run.root == Path("/test/workdir")


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


def test_request_from_config() -> None:
    req = Request.from_config({"method": "POST", "response": {"body": "hey"}})
    assert req.method == "POST"
    assert req.path == "/"
    assert req.response == Response(status=200, headers={}, body="hey")
    assert req.headers == {}
    assert req.body == ""


def test_request_from_config_with_body_and_headers() -> None:
    req = Request.from_config({
        "method": "POST",
        "path": "/echo",
        "headers": {"x-echo": "ping"},
        "body": "hello",
        "response": {"status": 200, "body": "hello"},
    })
    assert req.method == "POST"
    assert req.path == "/echo"
    assert req.headers == {"x-echo": "ping"}
    assert req.body == "hello"
    assert req.response == Response(status=200, headers={}, body="hello")


def test_request_from_config_rejects_non_dict_headers() -> None:
    with pytest.raises(ValueError):
        Request.from_config({"headers": "not-a-dict", "response": {}})


def test_request_from_config_rejects_non_str_body() -> None:
    with pytest.raises(ValueError):
        Request.from_config({"body": 123, "response": {}})


def test_endpoint_response_from_config_str_shorthand() -> None:
    response = EndpointResponse.from_config("hello")

    assert response.status == 200
    assert response.headers == {}
    assert response.body == "hello"


def test_endpoint_response_from_config_object() -> None:
    response = EndpointResponse.from_config({
        "status": 404,
        "headers": {"content-type": "text/plain"},
        "body": "nope",
    })

    assert response.status == 404
    assert response.headers == {"content-type": "text/plain"}
    assert response.body == "nope"


def test_endpoint_response_from_config_rejects_non_str_non_dict() -> None:
    with pytest.raises(ValueError, match="should be a str or an object"):
        EndpointResponse.from_config(42)


def test_endpoint_response_from_config_rejects_non_int_status() -> None:
    with pytest.raises(ValueError):
        EndpointResponse.from_config({"status": "200"})


def test_endpoint_from_config_with_defaults() -> None:
    endpoint = Endpoint.from_config({})

    assert endpoint.method == "GET"
    assert endpoint.path == "/"
    assert endpoint.response == EndpointResponse(status=200, headers={}, body="")


def test_endpoint_from_config_with_values() -> None:
    endpoint = Endpoint.from_config({
        "method": "PUT",
        "path": "/greet",
        "response": {"status": 201, "body": "hi"},
    })

    assert endpoint.method == "PUT"
    assert endpoint.path == "/greet"
    assert endpoint.response == EndpointResponse(status=201, headers={}, body="hi")


def test_endpoint_from_config_uppercases_method() -> None:
    endpoint = Endpoint.from_config({"method": "post", "path": "/greet"})

    assert endpoint.method == "POST"


def test_endpoint_from_config_rejects_unknown_method() -> None:
    with pytest.raises(ValueError, match="Unknown endpoint method: TRACE"):
        Endpoint.from_config({"method": "TRACE", "path": "/greet"})


def test_endpoint_from_config_rejects_non_str_method() -> None:
    with pytest.raises(ValueError, match="method should be a str"):
        Endpoint.from_config({"method": 1, "path": "/greet"})


def test_endpoint_from_config_rejects_non_str_path() -> None:
    with pytest.raises(ValueError, match="path should be a str"):
        Endpoint.from_config({"method": "GET", "path": 1})


def test_endpoint_from_config_echo_body_mode() -> None:
    endpoint = Endpoint.from_config(
        {"method": "POST", "path": "/echo", "mode": "echo-body"})

    assert endpoint.method == "POST"
    assert endpoint.path == "/echo"
    assert endpoint.response is None
    assert endpoint.mode == EndpointMode.ECHO_BODY


def test_endpoint_from_config_echo_body_mode_rejects_response() -> None:
    with pytest.raises(ValueError, match="'echo-body' mode takes no 'response'"):
        Endpoint.from_config(
            {"method": "POST", "path": "/echo", "mode": "echo-body", "response": "hi"})


def test_endpoint_from_config_echo_path_is_not_special() -> None:
    # The path is just a path; only `mode` selects behaviour.
    endpoint = Endpoint.from_config({"method": "POST", "path": "/echo"})

    assert endpoint.mode == EndpointMode.STATIC
    assert endpoint.response == EndpointResponse(status=200, headers={}, body="")


def test_endpoint_from_config_defaults_to_static_mode() -> None:
    endpoint = Endpoint.from_config({"path": "/greet", "response": "hello"})

    assert endpoint.mode == EndpointMode.STATIC
    assert endpoint.response == EndpointResponse(status=200, headers={}, body="hello")


def test_endpoint_from_config_echo_headers_mode() -> None:
    endpoint = Endpoint.from_config({"path": "/echo-headers", "mode": "echo-headers"})

    assert endpoint.mode == EndpointMode.ECHO_HEADERS
    assert endpoint.response is None


def test_endpoint_from_config_echo_headers_mode_rejects_response() -> None:
    with pytest.raises(ValueError, match="'echo-headers' mode takes no 'response'"):
        Endpoint.from_config({"path": "/echo-headers", "mode": "echo-headers", "response": "hi"})


def test_endpoint_from_config_rejects_unknown_mode() -> None:
    with pytest.raises(ValueError, match="Unknown endpoint mode"):
        Endpoint.from_config({"path": "/greet", "mode": "shout"})


def test_server_from_config_defaults_to_listening() -> None:
    server = Server.from_config(
        {"name": "main", "endpoints": [{"path": "/greet", "response": "hi"}]})

    assert server.name == "main"
    assert server.kind == ServerKind.LISTENING
    assert server.env_var == "HTTP_SERVER_MAIN"
    assert server.endpoints == [
        Endpoint(method="GET", path="/greet",
                 response=EndpointResponse(status=200, headers={}, body="hi"),
                 mode=EndpointMode.STATIC),
    ]


def test_server_from_config_closed_kind() -> None:
    server = Server.from_config({"name": "dead", "kind": "closed"})

    assert server.kind == ServerKind.CLOSED
    assert server.endpoints == []
    assert server.env_var == "HTTP_SERVER_DEAD"


def test_server_from_config_closed_kind_rejects_endpoints() -> None:
    with pytest.raises(ValueError, match="'closed' takes no 'endpoints'"):
        Server.from_config({"name": "dead", "kind": "closed", "endpoints": []})


@pytest.mark.parametrize("config", [
    {}, {"name": ""}, {"name": 1}, {"name": "has space"}, {"name": "has-dash"},
])
def test_server_from_config_rejects_bad_name(config: dict) -> None:
    with pytest.raises(ValueError, match="Server name should be"):
        Server.from_config(config)


def test_server_from_config_rejects_unknown_kind() -> None:
    with pytest.raises(ValueError, match="Unknown server kind"):
        Server.from_config({"name": "main", "kind": "haunted"})


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"servers": [{"name": "main", "endpoints":'
              ' [{"method": "post", "path": "/echo", "mode": "echo-body"}]},'
              ' {"name": "dead", "kind": "closed"}]}',
)
def test_new_config_with_servers(_mock_file: Mock) -> None:
    config = Config.from_file("file")

    assert config.servers == [
        Server(name="main", kind=ServerKind.LISTENING, endpoints=[
            Endpoint(method="POST", path="/echo", response=None,
                     mode=EndpointMode.ECHO_BODY),
        ]),
        Server(name="dead", kind=ServerKind.CLOSED, endpoints=[]),
    ]


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"servers": [{"name": "main"}, {"name": "MAIN"}]}',
)
def test_new_config_rejects_duplicate_server_names(_mock_file: Mock) -> None:
    with pytest.raises(ValueError, match="Duplicate server names"):
        Config.from_file("file")


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"operations": [{"type": "run"}, {"type": "wait"}]}',
)
def test_new_config_without_servers(_mock_file: Mock) -> None:
    config = Config.from_file("file")

    assert config.servers == []


def test_kill_from_config_with_signal() -> None:
    kill = Kill.from_config({"signal": "SIGABRT"})
    assert kill.signal == signal.SIGABRT


def test_kill_from_config_with_defaults() -> None:
    kill = Kill.from_config({})
    assert kill.signal == signal.SIGTERM


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"operations": [{"type": "run"}, {"type": "wait"}], "proposals": []}',
)
def test_new_config_with_empty_proposals(_mock_file: Mock) -> None:
    config = Config.from_file("file")

    assert len(config.proposals) == 0
    assert config.world == WasiWorld.CLI_COMMAND


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"operations": [{"type": "run"}], "proposals": ["http", "sockets"], "world": "wasi:http/service"}',
)
def test_new_config_with_multiple_proposals(_mock_file: Mock) -> None:
    config = Config.from_file("file")

    assert len(config.proposals) == 2
    assert config.proposals[0] == WasiProposal.HTTP
    assert config.proposals[1] == WasiProposal.SOCKETS
    assert config.world == WasiWorld.HTTP_SERVICE


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"operations": [{"type": "run"}], "proposals": ["invalid"]}',
)
def test_new_config_should_fail_with_invalid_proposal(_mock_file: Mock) -> None:
    with pytest.raises(ValueError):
        Config.from_file("file")


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"operations": [{"type": "run"}], world: "invalid"}',
)
def test_new_config_should_fail_with_invalid_world(_mock_file: Mock) -> None:
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


def test_dry_run_request_before_run() -> None:
    config = Config(operations=[Request.from_config({})])
    with pytest.raises(AssertionError, match="no process running"):
        validate_config(config)


def test_dry_run_multiple_errors() -> None:
    config = Config(operations=[Read(), Wait(), Run(), Run()])
    with pytest.raises(AssertionError) as exc_info:
        validate_config(config)
    error_message = str(exc_info.value)
    assert "no process running" in error_message
