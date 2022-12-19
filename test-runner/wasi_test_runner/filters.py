from typing import Tuple, Any
from abc import ABC
from abc import abstractmethod

import json


class TestFilter(ABC):
    @abstractmethod
    def should_skip(self, test_suite_name: str, test_name: str) -> Tuple[bool, Any]:
        pass


class JSONTestFilter(TestFilter):
    def __init__(self, filename: str) -> None:
        with open(filename, encoding="utf-8") as file:
            self.filter_dict = json.load(file)

    def should_skip(self, test_suite_name: str, test_name: str) -> Tuple[bool, Any]:
        test_suite_filter = self.filter_dict.get(test_suite_name)
        if test_suite_filter is None:
            return False, None
        why = test_suite_filter.get(test_name)
        return why is not None, why
