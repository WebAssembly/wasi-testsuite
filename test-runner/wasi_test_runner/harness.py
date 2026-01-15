from typing import List
from pathlib import Path

from .filters import (
    TestFilter, JSONTestExcludeFilter, UnsupportedWasiTestExcludeFilter
)
from .reporters import TestReporter
from .reporters.console import ConsoleTestReporter
from .reporters.json import JSONTestReporter
from .test_suite_runner import run_tests_from_test_suite
from .runtime_adapter import RuntimeAdapter


# too-many-positional-arguments is a post-3.0 pylint message.
# pylint: disable-msg=unknown-option-value
# pylint: disable-msg=too-many-arguments
# pylint: disable-msg=too-many-positional-arguments
def run_tests(runtimes: List[RuntimeAdapter],
              test_suite_paths: List[Path],
              exclude_filters: List[Path] | None = None,
              color: bool = True,
              verbose: bool = False,
              json_log_file: str | None = None) -> int:
    reporters: List[TestReporter] = [ConsoleTestReporter(color, verbose=verbose)]
    if json_log_file:
        reporters.append(JSONTestReporter(json_log_file))
    filters: List[TestFilter] = [UnsupportedWasiTestExcludeFilter()]
    if exclude_filters is not None:
        filters += [JSONTestExcludeFilter(str(filt)) for filt in exclude_filters]

    return run_all_tests(runtimes, [str(p) for p in test_suite_paths], reporters, filters)


def run_all_tests(
    runtimes: List[RuntimeAdapter],
    test_suite_paths: List[str],
    reporters: List[TestReporter],
    filters: List[TestFilter],
) -> int:
    ret = 0

    for test_suite_path in test_suite_paths:
        for runtime in runtimes:
            test_suite = run_tests_from_test_suite(
                test_suite_path, runtime, reporters, filters,
            )
            for reporter in reporters:
                reporter.report_test_suite(test_suite)
            if test_suite.fail_count > 0:
                ret = 1

    for reporter in reporters:
        reporter.finalize()

    return ret
