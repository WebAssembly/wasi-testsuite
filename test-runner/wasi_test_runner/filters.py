from abc import ABC
from abc import abstractmethod
from pathlib import Path
from typing import Any, Tuple, Union, Literal

import tomllib

from .test_suite import TestSuiteMeta
from .test_case import Config

VALID_ACTIONS = ["skip"]


class TestFilter(ABC):
    @abstractmethod
    def should_skip(
        self, meta: TestSuiteMeta, test_name: str, config: Config
    ) -> Union[Tuple[Literal[True], str], Tuple[Literal[False], Literal[None]]]:
        pass


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

    def should_skip(
        self, meta: TestSuiteMeta, test_name: str, config: Config
    ) -> Union[Tuple[Literal[True], str], Tuple[Literal[False], Literal[None]]]:
        skip_filter = self.lookup.get(meta.name)
        if skip_filter is None:
            return False, None
        if test_name in skip_filter:
            return True, "Skipped by expectation file"
        return False, None


def _load_toml_expectations(path: Path) -> dict[str, set[str]]:
    with open(path, "rb") as file:
        data = tomllib.load(file)

    version = data.get("version", 1)
    if version != 1:
        raise ValueError(f"Unsupported expectation file version: {version}")

    expectations: dict[str, set[str]] = {}
    for suite in _list_of_tables(data.get("suite", []), "suite"):
        suite_name = _required_string(suite, "name")
        skipped_tests: set[str] = set()
        for test in _list_of_tables(suite.get("test", []), "suite.test"):
            test_name = _required_string(test, "name")
            action = test.get("action")
            if action not in VALID_ACTIONS:
                raise ValueError(f"Expected 'action' to be one of {VALID_ACTIONS}, got {action!r}")
            skipped_tests.add(test_name)
        expectations[suite_name] = skipped_tests
    return expectations


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
