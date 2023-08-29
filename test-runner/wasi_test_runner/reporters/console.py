from typing import List
from colorama import Fore, init

from . import TestReporter
from ..test_case import TestCase
from ..test_suite import TestSuite
from ..runtime_adapter import RuntimeVersion


class ConsoleTestReporter(TestReporter):
    _PASS_COLOR: str = Fore.GREEN
    _FAIL_COLOR: str = Fore.RED
    _SKIP_COLOR: str = Fore.LIGHTBLACK_EX
    _RESET_COLOR: str = Fore.RESET

    def __init__(self, colored: bool = True) -> None:
        super().__init__()
        init(autoreset=True)
        self._test_suites: List[TestSuite] = []
        self._colored = colored

    def report_test(self, test: TestCase) -> None:
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

    def report_test_suite(self, test_suite: TestSuite) -> None:
        self._test_suites.append(test_suite)

    def finalize(self, version: RuntimeVersion) -> None:
        print("")
        print("===== Test results =====")
        print(f"Runtime: {version.name} {version.version}")

        total_skip = total_pass = total_fail = pass_suite = 0

        for suite in self._test_suites:
            total_pass += suite.pass_count
            total_fail += suite.fail_count
            total_skip += suite.skip_count

            if suite.fail_count == 0:
                pass_suite += 1

            print(f"Suite: {suite.name}")
            print(f"  Total: {suite.test_count}")
            self._print_pass(f"  Passed:  {suite.pass_count}")
            self._print_fail(f"  Failed:  {suite.fail_count}")
            self._print_skip(f"  Skipped: {suite.skip_count}")
            print("")

        print(
            f"Test suites: {self._get_summary(len(self._test_suites) - pass_suite, pass_suite, 0)}"
        )
        print(f"Tests:       {self._get_summary(total_fail, total_pass, total_skip)}")

    def _get_summary(self, fail_count: int, pass_count: int, skip_count: int) -> str:
        items: List[str] = []

        if fail_count:
            items.append(f"{self._fail_color}{fail_count} failed")
        if pass_count:
            items.append(f"{self._pass_color}{pass_count} passed")
        if skip_count:
            items.append(f"{self._skip_color}{skip_count} skipped")

        total = fail_count + pass_count + skip_count
        items.append(f"{self._reset_color}{total} total")
        return ", ".join(items)

    def _print_fail(self, text: str) -> None:
        print(f"{self._fail_color}{text}")

    def _print_pass(self, text: str) -> None:
        print(f"{self._pass_color}{text}")

    def _print_skip(self, text: str) -> None:
        print(f"{self._skip_color}{text}")

    @property
    def _skip_color(self) -> str:
        return self._SKIP_COLOR if self._colored else ""

    @property
    def _pass_color(self) -> str:
        return self._PASS_COLOR if self._colored else ""

    @property
    def _fail_color(self) -> str:
        return self._FAIL_COLOR if self._colored else ""

    @property
    def _reset_color(self) -> str:
        return self._RESET_COLOR if self._colored else ""
