from abc import ABC
from abc import abstractmethod
from pathlib import Path
from typing import Any, NamedTuple, Tuple, Union, Literal

import tomllib

from .test_suite import TestSuiteMeta
from .test_case import Config

SKIP_ACTION = "skip"
VALID_ACTIONS = [SKIP_ACTION]

EXPECTED_PASS = "pass"
EXPECTED_FAIL = "fail"
VALID_EXPECTED = [EXPECTED_PASS, EXPECTED_FAIL]


class _Expectation(NamedTuple):
    skip: bool = False
    expected_fail: bool = False


class TestFilter(ABC):
    @abstractmethod
    def should_skip(
        self, meta: TestSuiteMeta, test_name: str, config: Config
    ) -> Union[Tuple[Literal[True], str], Tuple[Literal[False], Literal[None]]]:
        pass

    def expected_to_fail(self, meta: TestSuiteMeta, test_name: str) -> bool:
        # Base filters have no opinion; only the expectation file marks xfail.
        del meta, test_name
        return False


class UnsupportedWasiTestExcludeFilter(TestFilter):
    def should_skip(
        self, meta: TestSuiteMeta, test_name: str, config: Config
    ) -> Union[Tuple[Literal[True], str], Tuple[Literal[False], Literal[None]]]:
        if meta.wasi_version not in meta.runtime.supported_wasi_versions:
            return True, "WASI version unsupported by runtime"
        if config.world not in meta.runtime.supported_wasi_worlds:
            return True, "WASI world unsupported by runtime"
        return False, None


class TestExpectationFilter(TestFilter):
    def __init__(self, filename: str) -> None:
        self.lookup = _load_toml_expectations(Path(filename))

    def _lookup(self, meta: TestSuiteMeta, test_name: str) -> _Expectation:
        return self.lookup.get(meta.name, {}).get(test_name, _Expectation())

    def should_skip(
        self, meta: TestSuiteMeta, test_name: str, config: Config
    ) -> Union[Tuple[Literal[True], str], Tuple[Literal[False], Literal[None]]]:
        if self._lookup(meta, test_name).skip:
            return True, "Skipped by expectation file"
        return False, None

    def expected_to_fail(self, meta: TestSuiteMeta, test_name: str) -> bool:
        return self._lookup(meta, test_name).expected_fail


def _load_toml_expectations(path: Path) -> dict[str, dict[str, _Expectation]]:
    with open(path, "rb") as file:
        data = tomllib.load(file)

    version = data.get("version", 1)
    if version != 1:
        raise ValueError(f"Unsupported expectation file version: {version}")

    expectations: dict[str, dict[str, _Expectation]] = {}
    for suite in _list_of_tables(data.get("suite", []), "suite"):
        suite_name = _required_string(suite, "name")
        tests: dict[str, _Expectation] = {}
        for test in _list_of_tables(suite.get("test", []), "suite.test"):
            test_name = _required_string(test, "name")
            tests[test_name] = _expectation_from_table(test)
        expectations[suite_name] = tests
    return expectations


def _expectation_from_table(test: dict[str, Any]) -> _Expectation:
    action = test.get("action")
    if action is not None and action not in VALID_ACTIONS:
        raise ValueError(f"Expected 'action' to be one of {VALID_ACTIONS}, got {action!r}")

    expected = test.get("expected")
    if expected is not None and expected not in VALID_EXPECTED:
        raise ValueError(f"Expected 'expected' to be one of {VALID_EXPECTED}, got {expected!r}")

    if action is None and expected is None:
        raise ValueError("Each test entry must set 'action' and/or 'expected'")

    return _Expectation(
        skip=action == SKIP_ACTION,
        expected_fail=expected == EXPECTED_FAIL,
    )


def _list_of_tables(value: Any, key: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"Expected '{key}' to be a list of tables")
    items: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError(f"Expected '{key}' to be a list of tables")
        items.append(item)
    return items


def _required_string(table: dict[str, Any], key: str) -> str:
    value = table.get(key)
    if not isinstance(value, str):
        raise ValueError(f"Expected '{key}' to be a string")
    return value
