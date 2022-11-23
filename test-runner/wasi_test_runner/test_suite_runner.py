import glob
import json
import os
import re
import time

from datetime import datetime
from typing import List, cast

from .runtime_adapter import RuntimeAdapter
from .test_case import (
    Result,
    Config,
    Output,
    TestCase,
)
from .reporters import TestReporter
from .test_suite import TestSuite
from .validators import Validator


def run_tests_from_test_suite(
    test_suite_path: str,
    runtime: RuntimeAdapter,
    validators: List[Validator],
    reporters: List[TestReporter],
) -> TestSuite:
    test_cases: List[TestCase] = []
    test_start = datetime.now()

    for test_path in glob.glob(os.path.join(test_suite_path, "*.wasm")):
        test_case = _execute_single_test(runtime, validators, test_path)
        test_cases.append(test_case)
        for reporter in reporters:
            reporter.report_test(test_case)

    elapsed = (datetime.now() - test_start).total_seconds()

    return TestSuite(
        name=_read_manifest(test_suite_path),
        time=test_start,
        duration_s=elapsed,
        test_cases=test_cases,
    )


def _execute_single_test(
    runtime: RuntimeAdapter, validators: List[Validator], test_path: str
) -> TestCase:
    config = _read_test_config(test_path)
    test_start = time.time()
    test_output = runtime.run_test(test_path, config.args, config.env, config.dirs)
    elapsed = time.time() - test_start

    return TestCase(
        name=os.path.splitext(os.path.basename(test_path))[0],
        config=config,
        result=_validate(validators, config, test_output),
        duration_s=elapsed,
    )


def _validate(validators: List[Validator], config: Config, output: Output) -> Result:
    failures = [
        result
        for result in [validator(config, output) for validator in validators]
        if result is not None
    ]

    return Result(failures=failures, is_executed=True, output=output)


def _read_test_config(test_path: str) -> Config:
    config_file = re.sub("\\.wasm$", ".json", test_path)
    if os.path.exists(config_file):
        return Config.from_file(config_file)
    return Config()


def _read_manifest(test_suite_path: str) -> str:
    manifest_path = os.path.join(test_suite_path, "manifest.json")
    if not os.path.exists(manifest_path):
        return test_suite_path
    with open(manifest_path, encoding="utf-8") as file:
        return cast(str, json.load(file)["name"])
