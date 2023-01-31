from typing import NamedTuple, List
from datetime import datetime
from .test_case import TestCase, Executed, Skipped


class TestSuite(NamedTuple):
    name: str
    duration_s: float
    time: datetime
    test_cases: List[TestCase]

    @property
    def test_count(self) -> int:
        return len(self.test_cases)

    @property
    def pass_count(self) -> int:
        return len(
            [
                1
                for test in self.test_cases
                if isinstance(test.result, Executed) and not test.result.failures
            ]
        )

    @property
    def fail_count(self) -> int:
        return len(
            [
                1
                for test in self.test_cases
                if isinstance(test.result, Executed) and test.result.failures
            ]
        )

    @property
    def skip_count(self) -> int:
        return len([1 for test in self.test_cases if isinstance(test.result, Skipped)])
