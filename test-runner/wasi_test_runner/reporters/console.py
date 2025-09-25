import shlex
from typing import List, Optional, Dict
from colorama import Fore, init

from . import TestReporter
from ..test_case import TestCase
from ..test_suite import TestSuite, TestSuiteMeta
from ..runtime_adapter import RuntimeMeta


class ConsoleTestReporter(TestReporter):
    _PASS_COLOR: str = Fore.GREEN
    _FAIL_COLOR: str = Fore.RED
    _SKIP_COLOR: str = Fore.LIGHTBLACK_EX
    _RESET_COLOR: str = Fore.RESET

    def __init__(self, colored: bool = True, verbose: bool = False) -> None:
        super().__init__()
        init(autoreset=True)
        self._test_suites: List[TestSuite] = []
        self._current_test_suite: Optional[TestSuiteMeta] = None
        self._colored = colored
        self._verbose = verbose

    def report_test(self, meta: TestSuiteMeta, test: TestCase) -> None:
        if self._current_test_suite is None:
            print(f"Running test suite {meta.name} with {meta.runtime}")
            self._current_test_suite = meta

        if self._verbose:
            self._report_test_verbose(test)
        else:
            self._report_test_terse(test)

    def _report_test_verbose(self, test: TestCase) -> None:
        if test.result.failed:
            self._print_fail(f"Test {test.name} failed")
            for reason in test.result.failures:
                self._print_fail(f"  [{reason.type}] {reason.message}")
            print("STDOUT:")
            print(test.result.output.stdout)
            print("STDERR:")
            print(test.result.output.stderr)
        elif test.result.is_executed:
            self._print_pass(f"Test {test.name} passed")
        else:
            self._print_skip(f"Test {test.name} skipped")

    def _report_test_terse(self, test: TestCase) -> None:
        if test.result.failed:
            print(self._fail_colored("!"), end='')
        elif test.result.is_executed:
            print(self._pass_colored("."), end='')
        else:
            print(self._skip_colored("_"), end='')

    def report_test_suite(self, test_suite: TestSuite) -> None:
        self._test_suites.append(test_suite)
        self._current_test_suite = None
        print("")

    def finalize(self) -> None:
        print("===== Test results =====")

        test_suites_by_runtime: Dict[RuntimeMeta, List[TestSuite]] = {}
        for suite in self._test_suites:
            if suite.meta.runtime not in test_suites_by_runtime:
                test_suites_by_runtime[suite.meta.runtime] = []
            test_suites_by_runtime[suite.meta.runtime].append(suite)

        for runtime, test_suites in test_suites_by_runtime.items():
            self._print_result_for_runtime(runtime, test_suites)

    def _print_result_for_runtime(self, runtime: RuntimeMeta,
                                  suites: List[TestSuite]) -> None:
        total_skip = total_pass = total_fail = 0

        for suite in suites:
            total_pass += suite.pass_count
            total_fail += suite.fail_count
            total_skip += suite.skip_count
        total_tests = total_pass + total_fail

        summary = f"{runtime.name} {runtime.version}: "
        if total_fail > 0:
            summary += self._fail_colored("FAIL")
            summary += f": {total_fail}/{total_tests} tests failed"
        elif total_pass > 0:
            summary += self._pass_colored("PASS")
            summary += f": {total_pass} tests passed"
        else:
            summary += self._skip_colored("SKIP")
            summary += ": all tests skipped"
        if total_skip > 0:
            summary += f" ({total_skip} skipped)"
        print(summary)

        for suite in suites:
            for test_case in suite.test_cases:
                if test_case.result.is_executed and test_case.result.failed:
                    print(f"  {shlex.join([str(a) for a in test_case.argv])}")

    def _colored_str(self, color: str, text: str) -> str:
        if self._colored:
            return f"{color}{text}{self._RESET_COLOR}"
        return text

    def _fail_colored(self, text: str) -> str:
        return self._colored_str(self._FAIL_COLOR, text)

    def _pass_colored(self, text: str) -> str:
        return self._colored_str(self._PASS_COLOR, text)

    def _skip_colored(self, text: str) -> str:
        return self._colored_str(self._SKIP_COLOR, text)

    def _print_fail(self, text: str) -> None:
        print(self._fail_colored(text))

    def _print_pass(self, text: str) -> None:
        print(self._pass_colored(text))

    def _print_skip(self, text: str) -> None:
        print(self._skip_colored(text))
