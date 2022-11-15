from typing import Any
from unittest.mock import ANY, MagicMock, Mock, patch, mock_open

import wasi_test_runner.test_case as tc
from wasi_test_runner import executor


def get_mock_open() -> Mock:
    def open_mock(filename: str, *_args: Any, **_kwargs: Any) -> Any:
        file_content = {
            "my-path/manifest.json": '{"name": "test-suite"}',
            "test1.json": "{}",
            "test2.json": '{"exit_code": 1, "args": ["a", "b"]}',
            "test3.json": '{"stdout": "output"}',
        }
        if filename in file_content:
            return mock_open(read_data=file_content[filename]).return_value

        raise FileNotFoundError(f"(mock) Unable to open {filename}")

    return MagicMock(side_effect=open_mock)


# pylint: disable-msg=too-many-locals
@patch("builtins.open", get_mock_open())
@patch("os.path.exists", Mock(return_value=True))
def test_executor_end_to_end() -> None:
    test_paths = ["test1.wasm", "test2.wasm", "test3.wasm"]

    failures = [tc.Failure("a", "b"), tc.Failure("x", "y"), tc.Failure("x", "z")]

    outputs = [
        tc.Output(0, "test1", ""),
        tc.Output(1, "test2", ""),
        tc.Output(2, "test3", ""),
    ]
    expected_results = [
        tc.Result(outputs[0], True, []),
        tc.Result(outputs[1], True, [failures[1]]),
        tc.Result(outputs[2], True, [failures[0], failures[2]]),
    ]
    expected_config = [
        tc.Config(),
        tc.Config(args=["a", "b"], exit_code=1),
        tc.Config(stdout="output"),
    ]

    expected_test_cases = [
        tc.TestCase(test_name, config, result, ANY)
        for config, test_name, result in zip(
            expected_config, ["test1", "test2", "test3"], expected_results
        )
    ]

    runtime = Mock()
    runtime.run_test.side_effect = outputs

    validators = [
        Mock(side_effect=[None, None, failures[0]]),
        Mock(side_effect=[None, failures[1], failures[2]]),
    ]

    reporters = [Mock(), Mock()]

    with patch("glob.glob", return_value=test_paths):
        suite = executor.TestSuiteExecutor("my-path", runtime, validators).run(  # type: ignore
            reporters  # type: ignore
        )

    # Assert manifest was read correctly
    assert suite.name == "test-suite"

    # Assert test cases
    assert suite.test_count == 3
    assert suite.test_cases == expected_test_cases

    # Assert test runner calls
    assert runtime.run_test.call_count == 3
    for test_path, config in zip(test_paths, expected_config):
        runtime.run_test.assert_any_call(test_path, config.args)

    # Assert reporters calls
    for reporter in reporters:
        assert reporter.report_test.call_count == 3
        for test_case in expected_test_cases:
            reporter.report_test.assert_any_call(test_case)

    # Assert validators calls
    for validator in validators:
        assert validator.call_count == 3
        for config, output in zip(expected_config, outputs):
            validator.assert_any_call(config, output)


@patch("os.path.exists", Mock(return_value=False))
def test_executor_should_use_path_for_name_if_manifest_does_not_exist() -> None:
    suite = executor.TestSuiteExecutor("my-path", Mock(), []).run([])

    assert suite.name == "my-path"
