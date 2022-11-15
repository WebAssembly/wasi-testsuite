from json import JSONDecodeError
from unittest.mock import Mock, patch, mock_open

import pytest

from wasi_test_runner.test_case import Config, Failure, Output, Result


@patch("builtins.open", new_callable=mock_open, read_data="{}")
def test_test_config_sholud_load_defaults_for_empty_json(_mock_file: Mock) -> None:
    config = Config.from_file("file")

    assert config.args == []
    assert config.exit_code == 0
    assert config.stdout is None
    assert config.wasi_functions == []


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"args": ["a", "b"], "exit_code": 5}',
)
def test_test_config_sholud_load_values_from_json(_mock_file: Mock) -> None:
    config = Config.from_file("file")

    assert config.exit_code == 5
    assert config.args == ["a", "b"]


@patch("builtins.open", new_callable=mock_open, read_data="not-json")
def test_test_config_sholud_fail_when_invalid_json(_mock_file: Mock) -> None:
    with pytest.raises(JSONDecodeError):
        Config.from_file("file")


@patch("builtins.open", new_callable=mock_open, read_data='{"invalid-field": 1}')
def test_test_config_should_warn_when_unknown_field(_mock_file: Mock) -> None:
    with patch("logging.warning") as mocked_logger:
        Config.from_file("file")
        mocked_logger.assert_called_once()


def test_test_results_should_mark_failed_if_multiple_failures() -> None:
    results = Result(Output(0, "", ""), True, [Failure("type", "message")])

    assert results.failed is True


def test_test_results_should_not_mark_failed_if_no_failure() -> None:
    results = Result(Output(0, "", ""), True, [])

    assert results.failed is False
