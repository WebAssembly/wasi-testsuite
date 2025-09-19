from typing import List
from pathlib import Path

from .filters import TestFilter, JSONTestExcludeFilter
from .reporters import TestReporter
from .reporters.console import ConsoleTestReporter
from .reporters.json import JSONTestReporter
from .test_suite_runner import run_tests_from_test_suite
from .runtime_adapter import RuntimeAdapter
from .validators import exit_code_validator, stdout_validator, Validator


def run_tests(runtimes: List[RuntimeAdapter],
              test_suite_paths: List[Path],
              exclude_filters: List[Path] | None = None,
              color: bool = True,
              json_log_file: str | None = None) -> int:
    validators: List[Validator] = [exit_code_validator, stdout_validator]
    reporters: List[TestReporter] = [ConsoleTestReporter(color)]
    if json_log_file:
        reporters.append(JSONTestReporter(json_log_file))
    filters: List[TestFilter] = []
    if exclude_filters is not None:
        filters = [JSONTestExcludeFilter(str(filt)) for filt in exclude_filters]

    return run_all_tests(runtimes, [str(p) for p in test_suite_paths],
                         validators, reporters, filters)


def run_all_tests(
    runtimes: List[RuntimeAdapter],
    test_suite_paths: List[str],
    validators: List[Validator],
    reporters: List[TestReporter],
    filters: List[TestFilter],
) -> int:
    ret = 0

    for test_suite_path in test_suite_paths:
        for runtime in runtimes:
            test_suite = run_tests_from_test_suite(
                test_suite_path, runtime, validators, reporters, filters,
            )
            for reporter in reporters:
                reporter.report_test_suite(test_suite)
            if test_suite.fail_count > 0:
                ret = 1

    for reporter in reporters:
        reporter.finalize()

    return ret
