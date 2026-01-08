import glob
import json
import os
import re
import time

from datetime import datetime
from pathlib import Path
from typing import List, NamedTuple

from .filters import TestFilter
from .runtime_adapter import RuntimeAdapter
from .test_case import (
    Result,
    Config,
    TestCase,
    WasiVersion
)
from .reporters import TestReporter
from .test_suite import TestSuite, TestSuiteMeta


class Manifest(NamedTuple):
    name: str
    wasi_version: WasiVersion


# pylint: disable-msg=too-many-locals
def run_tests_from_test_suite(
    test_suite_path: str,
    runtime: RuntimeAdapter,
    reporters: List[TestReporter],
    filters: List[TestFilter],
) -> TestSuite:
    test_cases: List[TestCase] = []
    test_start = datetime.now()

    manifest = _read_manifest(Path(test_suite_path))
    meta = TestSuiteMeta(manifest.name, manifest.wasi_version,
                         runtime.get_meta())

    for test_path in glob.glob(os.path.join(test_suite_path, "*.wasm")):
        test_name = os.path.splitext(os.path.basename(test_path))[0]
        for filt in filters:
            # for now, just drop the skip reason string. it might be
            # useful to make reporters report it.
            skip, _ = filt.should_skip(meta, test_name)
            if skip:
                test_case = _skip_single_test(runtime, meta, test_path)
                break
        else:
            test_case = _execute_single_test(runtime, meta, test_path)
        test_cases.append(test_case)
        for reporter in reporters:
            reporter.report_test(meta, test_case)

    elapsed = (datetime.now() - test_start).total_seconds()

    return TestSuite(
        meta=meta,
        time=test_start,
        duration_s=elapsed,
        test_cases=test_cases,
    )


def _skip_single_test(
    runtime: RuntimeAdapter, meta: TestSuiteMeta, test_path: str
) -> TestCase:
    config = _read_test_config(test_path)
    argv = runtime.compute_argv(test_path, config, meta.wasi_version)

    return TestCase(
        name=os.path.splitext(os.path.basename(test_path))[0],
        argv=argv,
        config=config,
        result=Result(argv=argv, is_executed=False, failures=[]),
        duration_s=0,
    )


def _execute_single_test(
    runtime: RuntimeAdapter, meta: TestSuiteMeta, test_path: str
) -> TestCase:
    config = _read_test_config(test_path)
    test_start = time.time()
    result = runtime.run_test(test_path, config, meta.wasi_version)
    elapsed = time.time() - test_start

    return TestCase(
        name=os.path.splitext(os.path.basename(test_path))[0],
        argv=result.argv,
        config=config,
        result=result,
        duration_s=elapsed,
    )


def _read_test_config(test_path: str) -> Config:
    config_file = re.sub("\\.wasm$", ".json", test_path)
    if os.path.exists(config_file):
        return Config.from_file(config_file)
    return Config()


def _read_manifest(test_suite_path: Path) -> Manifest:
    manifest_path = test_suite_path / "manifest.json"
    if test_suite_path.name in WasiVersion:
        name = str(test_suite_path.parent)
        wasi_version = WasiVersion(test_suite_path.name)
    else:
        name = str(test_suite_path)
        wasi_version = WasiVersion.WASM32_WASIP1

    if manifest_path.exists():
        with open(str(manifest_path), encoding="utf-8") as file:
            contents = json.load(file)
            assert isinstance(contents, dict)
            for k, v in contents.items():
                match k:
                    case "name":
                        assert isinstance(v, str)
                        name = v
                    case "version":
                        assert v in WasiVersion
                        wasi_version = WasiVersion[v]
                    case _:
                        raise RuntimeError(f"unexpected manifest option: {k}={v}")

    return Manifest(name=name, wasi_version=wasi_version)
