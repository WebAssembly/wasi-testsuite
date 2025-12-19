import glob
import json
import os
import re
import shutil
import time

from datetime import datetime
from pathlib import Path
from typing import List, Tuple, NamedTuple

from .filters import TestFilter
from .runtime_adapter import RuntimeAdapter
from .test_case import (
    Result,
    Config,
    Output,
    TestCase,
    WasiVersion
)
from .reporters import TestReporter
from .test_suite import TestSuite, TestSuiteMeta
from .validators import Validator


class Manifest(NamedTuple):
    name: str
    wasi_version: WasiVersion


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
            test_case = _execute_single_test(runtime, meta, validators,
                                             test_path)
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
    config, _dir_pairs, argv = _prepare_test(runtime, meta.wasi_version,
                                             test_path)
    return TestCase(
        name=os.path.splitext(os.path.basename(test_path))[0],
        argv=argv,
        config=config,
        result=Result(output=Output(0, "", "", ""), is_executed=False, failures=[]),
        duration_s=0,
    )


def _execute_single_test(
    runtime: RuntimeAdapter, meta: TestSuiteMeta, validators: List[Validator],
    test_path: str
) -> TestCase:
    config, dir_pairs, argv = _prepare_test(runtime, meta.wasi_version,
                                            test_path)
    _cleanup_test_output(dir_pairs)
    test_start = time.time()
    test_output = runtime.run_test(argv, config)
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
    runtime: RuntimeAdapter, wasi_version: WasiVersion, test_path: str
) -> Tuple[Config, List[Tuple[Path, str]], List[str]]:
    config = _read_test_config(test_path)
    dir_pairs = [(Path(test_path).parent / d, d) for d in config.dirs]
    argv = runtime.compute_argv(test_path, config.args, config.env, dir_pairs,
                                wasi_version)
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


def _cleanup_test_output(dirs: List[Tuple[Path, str]]) -> None:
    for host, _guest in dirs:
        for f in host.glob("**/*.cleanup"):
            if f.is_file():
                f.unlink()
            elif f.is_dir():
                shutil.rmtree(f)
