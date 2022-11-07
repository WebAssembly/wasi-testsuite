from typing import Callable, Optional

from .test_case import TestOutput, TestConfig, Failure

Validator = Callable[[TestConfig, TestOutput], Optional[Failure]]


def exit_code_validator(config: TestConfig, output: TestOutput) -> Optional[Failure]:
    if config.exit_code == output.exit_code:
        return None
    return Failure("exit_code", f"{config.exit_code} == {output.exit_code}")


def stdout_validator(config: TestConfig, output: TestOutput) -> Optional[Failure]:
    if config.stdout is None or config.stdout == output.stdout:
        return None
    return Failure("stdout", f"{config.stdout} == {output.stdout}")
