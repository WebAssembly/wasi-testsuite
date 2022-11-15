from typing import Callable, Optional

from .test_case import Output, Config, Failure

Validator = Callable[[Config, Output], Optional[Failure]]


def exit_code_validator(config: Config, output: Output) -> Optional[Failure]:
    if config.exit_code == output.exit_code:
        return None
    return Failure("exit_code", f"{config.exit_code} == {output.exit_code}")


def stdout_validator(config: Config, output: Output) -> Optional[Failure]:
    if config.stdout is None or config.stdout == output.stdout:
        return None
    return Failure("stdout", f"{config.stdout} == {output.stdout}")
