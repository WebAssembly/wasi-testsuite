from typing import Tuple, Union, Literal
from abc import ABC
from abc import abstractmethod

import json

from .test_suite import TestSuiteMeta


class TestFilter(ABC):
    @abstractmethod
    def should_skip(
        self, meta: TestSuiteMeta, test_name: str
    ) -> Union[Tuple[Literal[True], str], Tuple[Literal[False], Literal[None]]]:
        pass


class UnsupportedWasiTestExcludeFilter(TestFilter):
    def should_skip(
        self, meta: TestSuiteMeta, test_name: str
    ) -> Union[Tuple[Literal[True], str], Tuple[Literal[False], Literal[None]]]:
        if meta.wasi_version not in meta.runtime.supported_wasi_versions:
            return True, "WASI version unsupported by runtime"
        return False, None


class JSONTestExcludeFilter(TestFilter):
    def __init__(self, filename: str) -> None:
        with open(filename, encoding="utf-8") as file:
            self.filter_dict = json.load(file)

    def should_skip(
        self, meta: TestSuiteMeta, test_name: str
    ) -> Union[Tuple[Literal[True], str], Tuple[Literal[False], Literal[None]]]:
        test_suite_filter = self.filter_dict.get(meta.name)
        if test_suite_filter is None:
            return False, None
        why = test_suite_filter.get(test_name)
        if why is not None:
            return True, why
        return False, None
