from typing import Any
from pathlib import Path
from unittest.mock import ANY, MagicMock, Mock, patch, mock_open

import wasi_test_runner.test_suite as ts
import wasi_test_runner.test_case as tc
import wasi_test_runner.test_suite_runner as tsr
from wasi_test_runner.runtime_adapter import RuntimeMeta


def get_mock_open() -> Mock:
    def open_mock(filename: str, *_args: Any, **_kwargs: Any) -> Any:
        file_content = {
            "my-path/manifest.json": '{"name": "test-suite"}',
            "my-path/test1.json": '{"dirs": [".", "deep/dir"]}',
            "my-path/test2.json": '{"exit_code": 1, "args": ["a", "b"]}',
            "my-path/test3.json": '{"stdout": "output", "env": {"x": "1"}}',
            "my-path/test4.json": (
                '{"operations": [{"type": "run"}, {"type": "wait", "exit_code": 1}], '
                '"proposals": []}'
            ),
        }
        if filename in file_content:
            return mock_open(read_data=file_content[filename]).return_value

        raise FileNotFoundError(f"(mock) Unable to open {filename}")

    return MagicMock(side_effect=open_mock)


# pylint: disable-msg=too-many-locals
@patch("builtins.open", get_mock_open())
@patch("os.path.exists", Mock(return_value=True))
@patch("pathlib.Path.exists", Mock(return_value=True))
def test_runner_end_to_end() -> None:
    test_suite_dir = "my-path"
    test_suite_name = "test-suite"
    test_files = ["test1.wasm", "test2.wasm", "test3.wasm", "test4.wasm"]
    test_paths = [Path(test_suite_dir) / f for f in test_files]

    test_dirs = [".", "deep/dir"]
    runtime_name = "rt1"

    expected_argv = [runtime_name, "<test>"]
    expected_results = [
        tc.Result(True, []),
        tc.Result(True, [ANY]),
        tc.Result(True, [ANY, ANY]),
        tc.Result(True, [ANY])
    ]
    expected_config = [
        tc.Config(
            operations=[
                tc.Run(dirs=[(Path(test_suite_dir) / d, d) for d in test_dirs]),
                tc.Wait(exit_code=0)
            ],
            proposals=[]
        ),
        tc.Config(
            operations=[tc.Run(args=["a", "b"]), tc.Wait(exit_code=1)],
            proposals=[]
        ),
        tc.Config(
            operations=[tc.Run(env={"x": "1"}), tc.Read(id="stdout", payload="output"), tc.Wait(exit_code=0)],
            proposals=[]
        ),
        tc.Config(
            operations=[tc.Run(), tc.Wait(exit_code=1)],
            proposals=[]
        ),
    ]

    runtime_version_str = "4.2"
    the_runtime_wasi_version = tc.WasiVersion.WASM32_WASIP1
    runtime_wasi_versions = frozenset([the_runtime_wasi_version])
    runtime_meta = RuntimeMeta(runtime_name, runtime_version_str,
                               runtime_wasi_versions)

    expected_test_suite_meta = ts.TestSuiteMeta(test_suite_name,
                                                the_runtime_wasi_version,
                                                runtime_meta)

    expected_test_cases = [
        tc.TestCase(test_name, expected_argv, config, result, ANY)
        for config, test_name, result in zip(
            expected_config, ["test1", "test2", "test3", "test4"], expected_results
        )
    ]

    runtime = Mock()
    runtime.get_name.return_value = runtime_name
    runtime.get_meta.return_value = runtime_meta
    runtime.compute_argv.return_value = expected_argv

    reporters = [Mock(), Mock()]

    filt = Mock()
    filt.should_skip.return_value = (False, None)
    filters = [filt]

    process = Mock()
    process.stdin = mock_open().return_value
    process.stdout = mock_open(read_data='').return_value
    process.stderr = mock_open(read_data='').return_value
    process.returncode = 0
    process.communicate.return_value = ('', '')

    with (patch("glob.glob", return_value=[str(p) for p in test_paths]),
          patch("wasi_test_runner.test_suite_runner._cleanup_test_output"),
          patch("subprocess.Popen", return_value=process)):
        suite = tsr.run_tests_from_test_suite(test_suite_dir, runtime,
                                              reporters,   # type: ignore
                                              filters)     # type: ignore

    # Assert manifest was read correctly
    assert suite.meta == expected_test_suite_meta

    # Assert test cases
    assert suite.test_count == 4
    assert suite.test_cases == expected_test_cases

    # Assert test runner calls
    assert process.communicate.call_count == 4

    # Assert reporters calls
    for reporter in reporters:
        assert reporter.report_test.call_count == 4
        for test_case in expected_test_cases:
            reporter.report_test.assert_any_call(expected_test_suite_meta,
                                                 test_case)

    # Assert filter calls
    for filt in filters:
        assert filt.should_skip.call_count == 4
        for test_case in expected_test_cases:
            filt.should_skip.assert_any_call(expected_test_suite_meta,
                                             test_case.name)


@patch("os.path.exists", Mock(return_value=False))
def test_runner_should_use_path_for_name_if_manifest_does_not_exist() -> None:
    suite = tsr.run_tests_from_test_suite("my-path", Mock(), [], [])

    assert suite.meta.name == "my-path"
