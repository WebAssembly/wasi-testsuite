import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from adapters import wasm2go

def test_get_name():
    assert wasm2go.get_name() == "wasm2go"

def test_get_wasi_versions():
    assert wasm2go.get_wasi_versions() == ["wasm32-wasip1"]

def test_get_wasi_worlds():
    assert wasm2go.get_wasi_worlds() == ["wasi:cli/command"]

def test_compute_argv_basic():
    test_path = "foo.wasm"
    args = ["a"]
    env = {"K": "V"}
    dirs = [(Path("/h"), "g")]
    proposals = []
    wasi_world = "wasi:cli/command"
    wasi_version = "wasm32-wasip1"

    argv = wasm2go.compute_argv(test_path, (args, env, dirs), proposals, wasi_world, wasi_version)
    
    expected = ["wasm2go-run", "--env", "K=V", "--dir", "/h::g", "foo.wasm", "a"]
    assert argv == expected

def test_compute_argv_with_env_override():
    from pathlib import Path
    import adapters.wasm2go as wasm2go
    with patch.object(wasm2go, "WASM2GO_RUN", ["my-runner"]):
        argv = wasm2go.compute_argv("foo.wasm", ([], {}, []), [], "wasi:cli/command", "wasm32-wasip1")
        assert argv[0] == "my-runner"

@patch("subprocess.run")
def test_get_version_with_multi_token_prefix(mock_run):
    mock_run.return_value = MagicMock(stdout="v1.2.3\n")
    
    with patch.object(wasm2go, "WASM2GO_RUN", ["sudo", "-u", "nobody", "wasm2go-run"]):
        version = wasm2go.get_version()
        
    assert version == "v1.2.3"
    expected_args = ["sudo", "-u", "nobody", "wasm2go-run", "--version"]
    mock_run.assert_called_once_with(
        expected_args,
        capture_output=True,
        text=True,
        check=True
    )

@patch("subprocess.run")
def test_get_version(mock_run):
    mock_run.return_value = MagicMock(stdout="wasm2go-run version 0.1.0\n")
    version = wasm2go.get_version()
    assert version == "wasm2go-run version 0.1.0"
    mock_run.assert_called_once()
    assert mock_run.call_args.args[0] == wasm2go.WASM2GO_RUN + ["--version"]
