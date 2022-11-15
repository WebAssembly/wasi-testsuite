from abc import ABC

from ..test_case import TestCase
from ..test_suite import TestSuite
from ..runtime_adapter import RuntimeVersion


class TestReporter(ABC):
    def report_test(self, test: TestCase) -> None:
        pass

    def report_test_suite(self, test_suite: TestSuite) -> None:
        pass

    def finalize(self, version: RuntimeVersion) -> None:
        pass
