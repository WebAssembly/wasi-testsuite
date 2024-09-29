import json

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from .test_case import (
    Config,
)


class ConfigOverride(ABC):
    @abstractmethod
    def get_test_override(
        self, test_suite_name: str, test_name: str
    ) -> Optional[Config]:
        pass


class JSONConfigOverride(ConfigOverride):
    overrides_dict: Dict[str, Dict[str, Dict[str, Any]]]

    def __init__(self, overrides_path: str) -> None:
        with open(overrides_path, encoding="utf-8") as file:
            self.overrides_dict = json.load(file)

    def get_test_override(
        self, test_suite_name: str, test_name: str
    ) -> Optional[Config]:
        test_suite_overrides = self.overrides_dict.get(test_suite_name)

        if test_suite_overrides is None:
            return None

        test_override = test_suite_overrides.get(test_name)

        if test_override is None:
            return None

        return Config.from_dict(test_override)
