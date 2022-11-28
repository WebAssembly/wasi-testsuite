import json
from datetime import datetime
from typing import List


from . import TestReporter
from ..test_suite import TestSuite
from ..runtime_adapter import RuntimeVersion


class JSONTestReporter(TestReporter):
    def __init__(self, output_path: str) -> None:
        super().__init__()
        self._start_timestamp = datetime.utcnow()
        self._output_path = output_path
        self._test_suites: List[TestSuite] = []

    def report_test_suite(self, test_suite: TestSuite) -> None:
        self._test_suites.append(test_suite)

    def finalize(self, version: RuntimeVersion) -> None:
        results = []

        for suite in self._test_suites:
            results.append(
                {
                    "name": suite.name,
                    "duration_s": suite.duration_s,
                    "failed": suite.fail_count,
                    "skipped": suite.skip_count,
                    "passed": suite.pass_count,
                    "tests": [
                        {
                            "name": test.name,
                            "executed": test.result.is_executed,
                            "duration_s": test.duration_s,
                            "wasi_functions": test.config.wasi_functions,
                            "failures": [
                                failure.message for failure in test.result.failures
                            ],
                        }
                        for test in suite.test_cases
                    ],
                }
            )

        with open(self._output_path, "w", encoding="UTF-8") as file:
            json.dump(
                {
                    "execution": {
                        "start_timestamp": self._to_iso8601(self._start_timestamp),
                        "finish_timestamp": self._to_iso8601(datetime.utcnow())
                    },
                    "runtime": {"name": version.name, "version": version.version},
                    "results": results,
                },
                file,
                default=str,
            )

    @staticmethod
    def _to_iso8601(timestamp: datetime) -> str:
        return f"{timestamp.isoformat()[:-3]}Z"
