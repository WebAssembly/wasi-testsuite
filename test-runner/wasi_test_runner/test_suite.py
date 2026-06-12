from typing import NamedTuple, List
from datetime import datetime
from .test_case import TestCase, WasiVersion, Outcome
from .runtime_adapter import RuntimeMeta


class TestSuiteMeta(NamedTuple):
    name: str
    wasi_version: WasiVersion
    runtime: RuntimeMeta


class TestSuite(NamedTuple):
    meta: TestSuiteMeta
    duration_s: float
    time: datetime
    test_cases: List[TestCase]

    def _count(self, *outcomes: Outcome) -> int:
        return len([1 for test in self.test_cases if test.outcome in outcomes])

    @property
    def test_count(self) -> int:
        return len(self.test_cases)

    @property
    def pass_count(self) -> int:
        # Expected failures (xfail) count as passing: they matched the expectation.
        return self._count(Outcome.PASS, Outcome.XFAIL)

    @property
    def fail_count(self) -> int:
        # Regressions (fail) and stale expectations (xpass) both fail the suite.
        return self._count(Outcome.FAIL, Outcome.XPASS)

    @property
    def skip_count(self) -> int:
        return self._count(Outcome.SKIP)

    @property
    def xfail_count(self) -> int:
        return self._count(Outcome.XFAIL)

    @property
    def xpass_count(self) -> int:
        return self._count(Outcome.XPASS)
