from typing import NamedTuple, List
from datetime import datetime
from .test_case import TestCase


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
                if test.result.is_executed and test.result.failed is False
            ]
        )

    @property
    def fail_count(self) -> int:
        return len(
            [
                1
                for test in self.test_cases
                if test.result.is_executed and test.result.failed
            ]
        )

    @property
    def skip_count(self) -> int:
        return len([1 for test in self.test_cases if not test.result.is_executed])
