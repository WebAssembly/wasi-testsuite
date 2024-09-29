from typing import List, Optional

from .filters import TestFilter
from .reporters import TestReporter
from .test_suite_runner import run_tests_from_test_suite
from .runtime_adapter import RuntimeAdapter
from .validators import Validator
from .override import ConfigOverride


# pylint: disable-msg=too-many-arguments
def run_all_tests(
    runtime: RuntimeAdapter,
    test_suite_paths: List[str],
    validators: List[Validator],
    reporters: List[TestReporter],
    filters: List[TestFilter],
    override: Optional[ConfigOverride],
) -> int:
    ret = 0

    for test_suite_path in test_suite_paths:
        test_suite = run_tests_from_test_suite(
            test_suite_path, runtime, validators, reporters, filters, override
        )
        for reporter in reporters:
            reporter.report_test_suite(test_suite)
        if test_suite.fail_count > 0:
            ret = 1

    for reporter in reporters:
        reporter.finalize(runtime.get_version())

    return ret
