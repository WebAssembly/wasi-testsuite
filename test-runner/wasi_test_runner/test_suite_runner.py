import glob
import json
import os
import re
import shutil
import time

from datetime import datetime
from pathlib import Path
from typing import List, cast, Tuple

from .filters import TestFilter
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


# pylint: disable-msg=too-many-locals
def run_tests_from_test_suite(
    test_suite_path: str,
    runtime: RuntimeAdapter,
    validators: List[Validator],
    reporters: List[TestReporter],
    filters: List[TestFilter],
) -> TestSuite:
    test_cases: List[TestCase] = []
    test_start = datetime.now()

    test_suite_name = _read_manifest(test_suite_path)
    runtime_version = runtime.get_version()

    for test_path in glob.glob(os.path.join(test_suite_path, "*.wasm")):
        test_name = os.path.splitext(os.path.basename(test_path))[0]
        for filt in filters:
            # for now, just drop the skip reason string. it might be
            # useful to make reporters report it.
            skip, _ = filt.should_skip(runtime_version, test_suite_name,
                                       test_name)
            if skip:
                test_case = _skip_single_test(runtime, validators, test_path)
                break
        else:
            test_case = _execute_single_test(runtime, validators, test_path)
        test_cases.append(test_case)
        for reporter in reporters:
            reporter.report_test(test_suite_name, runtime_version, test_case)

    elapsed = (datetime.now() - test_start).total_seconds()

    return TestSuite(
        name=test_suite_name,
        runtime=runtime.get_version(),
        time=test_start,
        duration_s=elapsed,
        test_cases=test_cases,
    )


def _skip_single_test(
    runtime: RuntimeAdapter, _validators: List[Validator], test_path: str
) -> TestCase:
    config, _dir_pairs, argv = _prepare_test(runtime, test_path)
    return TestCase(
        name=os.path.splitext(os.path.basename(test_path))[0],
        argv=argv,
        config=config,
        result=Result(output=Output(0, "", ""), is_executed=False, failures=[]),
        duration_s=0,
    )


def _execute_single_test(
    runtime: RuntimeAdapter, validators: List[Validator], test_path: str
) -> TestCase:
    config, dir_pairs, argv = _prepare_test(runtime, test_path)
    _cleanup_test_output(dir_pairs)
    test_start = time.time()
    test_output = runtime.run_test(argv)
    elapsed = time.time() - test_start
    _cleanup_test_output(dir_pairs)

    return TestCase(
        name=os.path.splitext(os.path.basename(test_path))[0],
        argv=argv,
        config=config,
        result=_validate(validators, config, test_output),
        duration_s=elapsed,
    )


def _prepare_test(
    runtime: RuntimeAdapter, test_path: str
) -> Tuple[Config, List[Tuple[Path, str]], List[str]]:
    config = _read_test_config(test_path)
    dir_pairs = [(Path(test_path).parent / d, d) for d in config.dirs]
    argv = runtime.compute_argv(test_path, config.args, config.env, dir_pairs)
    return config, dir_pairs, argv


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


def _cleanup_test_output(dirs: List[Tuple[Path, str]]) -> None:
    for host, _guest in dirs:
        for f in host.glob("**/*.cleanup"):
            if f.is_file():
                f.unlink()
            elif f.is_dir():
                shutil.rmtree(f)
