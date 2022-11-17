import argparse
import sys
from typing import List


from .test_suite_location import get_test_suite_location
from .runtime_adapter import RuntimeAdapter
from .harness import run_all_tests
from .reporters import TestReporter
from .reporters.console import ConsoleTestReporter
from .reporters.json import JSONTestReporter
from .validators import exit_code_validator, stdout_validator, Validator


def main() -> int:
    parser = argparse.ArgumentParser(
        description="WebAssembly System Interface test executor"
    )

    parser.add_argument(
        "-t",
        "--test-suite",
        required=True,
        nargs="+",
        help="Locations of suites (directories with *.wasm test files or urls to ZIP archives).",
    )
    parser.add_argument(
        "-r", "--runtime-adapter", required=True, help="Path to a runtime adapter."
    )
    parser.add_argument(
        "--json-output-location",
        help="JSON test result destination. If not specified, JSON output won't be generated.",
    )
    parser.add_argument(
        "--disable-colors",
        action="store_true",
        default=False,
        help="Disables color for console output reporter.",
    )

    options = parser.parse_args()

    reporters: List[TestReporter] = [ConsoleTestReporter(not options.disable_colors)]
    if options.json_output_location:
        reporters.append(JSONTestReporter(options.json_output_location))

    validators: List[Validator] = [exit_code_validator, stdout_validator]

    return run_all_tests(
        RuntimeAdapter(options.runtime_adapter),
        [get_test_suite_location(suite) for suite in options.test_suite],
        validators,
        reporters,
    )


if __name__ == "__main__":
    sys.exit(main())
