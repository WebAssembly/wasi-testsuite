import glob
import json
import os
import re
import time

from datetime import datetime
from typing import List, cast

from .runtime_adapter import RuntimeAdapter
from .test_case import (
    TestResult,
    TestConfig,
    TestOutput,
    TestCase,
)
from .test_reporters import TestReporter
from .test_suite import TestSuite
from .validators import Validator


class TestSuiteExecutor:  # pylint: disable=too-few-public-methods
    def __init__(
        self, test_suite_path: str, runtime: RuntimeAdapter, validators: List[Validator]
    ) -> None:
        self._test_suite_path = test_suite_path
        self._runtime = runtime
        self._validators = validators
        self._test_suite_name = self._read_manifest()

    def run(self, reporters: List[TestReporter]) -> TestSuite:
        test_cases: List[TestCase] = []

        test_start = datetime.now()
        for test_path in glob.glob(os.path.join(self._test_suite_path, "*.wasm")):
            test_case = self._execute_single_test(test_path)
            test_cases.append(test_case)
            for reporter in reporters:
                reporter.report_test(test_case)
        elapsed = (datetime.now() - test_start).total_seconds()

        return TestSuite(
            name=self._test_suite_name,
            time=test_start,
            duration_s=elapsed,
            test_cases=test_cases,
        )

    def _execute_single_test(self, test_path: str) -> TestCase:
        config = self._read_test_config(test_path)

        test_start = time.time()
        test_output = self._runtime.run_test(test_path, config.args)
        elapsed = time.time() - test_start

        return TestCase(
            name=os.path.splitext(os.path.basename(test_path))[0],
            config=config,
            result=self._validate(config, test_output),
            duration_s=elapsed,
        )

    def _validate(self, config: TestConfig, output: TestOutput) -> TestResult:
        failures = [
            result
            for result in [validator(config, output) for validator in self._validators]
            if result is not None
        ]

        return TestResult(
            failures=failures,
            is_executed=True,
            output=output,
        )

    def _read_manifest(self) -> str:
        manifest_path = os.path.join(self._test_suite_path, "manifest.json")
        if not os.path.exists(manifest_path):
            return self._test_suite_path
        with open(manifest_path, encoding="utf-8") as file:
            return cast(str, json.load(file)["name"])

    def _read_test_config(self, test_path: str) -> TestConfig:
        config_file = re.sub("\\.wasm$", ".json", test_path)
        if os.path.exists(config_file):
            return TestConfig.from_file(config_file)
        return TestConfig()
