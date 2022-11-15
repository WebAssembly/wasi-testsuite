from wasi_test_runner.test_case import Config, Output
from wasi_test_runner.validators import stdout_validator, exit_code_validator


def test_stdout_validator_should_fail_if_stdout_differs() -> None:
    config = Config(stdout="x")
    output = Output(0, "y", "")
    assert stdout_validator(config, output) is not None


def test_stdout_validator_should_not_fail_if_stdout_matches() -> None:
    config = Config(stdout="x")
    output = Output(0, "x", "")
    assert stdout_validator(config, output) is None


def test_exit_code_validator_should_fail_if_exit_code_differs() -> None:
    config = Config(exit_code=1)
    output = Output(0, "", "")
    assert exit_code_validator(config, output) is not None


def test_exit_code_validator_should_not_fail_if_exit_code_matches() -> None:
    config = Config(exit_code=4)
    output = Output(4, "x", "")
    assert exit_code_validator(config, output) is None
