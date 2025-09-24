from abc import ABC

from ..test_case import TestCase
from ..test_suite import TestSuite, TestSuiteMeta


class TestReporter(ABC):
    def report_test(self, meta: TestSuiteMeta, test: TestCase) -> None:
        pass

    def report_test_suite(self, test_suite: TestSuite) -> None:
        pass

    def finalize(self) -> None:
        pass
