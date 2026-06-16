from datetime import datetime

import wasi_test_runner.test_case as tc
import wasi_test_runner.test_suite as ts
from wasi_test_runner.runtime_adapter import RuntimeMeta


def create_test_case(name: str, is_executed: bool, is_failed: bool,
                     expected_to_fail: bool = False) -> tc.TestCase:
    failures = [tc.Failure("a", "b")] if is_failed else []
    result = tc.Result(is_executed, failures)
    return tc.TestCase(
        name,
        ["test-runtime-exe", name],
        tc.Config(),
        result,
        1.0,
        tc.Outcome.evaluate(expected_to_fail, result),
    )


def test_test_suite_should_return_correct_count() -> None:
    suite = ts.TestSuite(
        ts.TestSuiteMeta("suite",
                         tc.WasiVersion.WASM32_WASIP1,
                         RuntimeMeta("test-runtime", "3.14",
                                     frozenset([tc.WasiVersion.WASM32_WASIP1]),
                                     frozenset([tc.WasiWorld.CLI_COMMAND]))),
        10.0,
        datetime.now(),
        [
            create_test_case("t1", True, True),
            create_test_case("t2", True, False),
            create_test_case("t3", False, True),
            create_test_case("t4", False, False),
        ],
    )

    assert suite.test_count == 4
    assert suite.skip_count == 2

    # Skipped tests are ignored
    assert suite.fail_count == 1
    assert suite.pass_count == 1


def test_test_suite_counts_xfail_as_pass_and_xpass_as_fail() -> None:
    suite = ts.TestSuite(
        ts.TestSuiteMeta("suite",
                         tc.WasiVersion.WASM32_WASIP1,
                         RuntimeMeta("test-runtime", "3.14",
                                     frozenset([tc.WasiVersion.WASM32_WASIP1]),
                                     frozenset([tc.WasiWorld.CLI_COMMAND]))),
        10.0,
        datetime.now(),
        [
            create_test_case("pass", True, False),
            create_test_case("regression", True, True),
            create_test_case("xfail", True, True, expected_to_fail=True),
            create_test_case("xpass", True, False, expected_to_fail=True),
        ],
    )

    assert suite.xfail_count == 1
    assert suite.xpass_count == 1
    # xfail counts as a pass, xpass counts as a fail.
    assert suite.pass_count == 2
    assert suite.fail_count == 2
