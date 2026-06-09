from pathlib import Path

from wasi_test_runner.filters import TestExpectationFilter as ExpectationFilter
from wasi_test_runner.runtime_adapter import RuntimeMeta
from wasi_test_runner.test_case import Config, WasiVersion, WasiWorld
from wasi_test_runner.test_suite import TestSuiteMeta as SuiteMeta


def _meta() -> SuiteMeta:
    return SuiteMeta(
        name="WASI Rust tests [wasm32-wasip3]",
        wasi_version=WasiVersion.WASM32_WASIP3,
        runtime=RuntimeMeta(
            name="runtime",
            version="1.0.0",
            supported_wasi_versions=frozenset([WasiVersion.WASM32_WASIP3]),
            supported_wasi_worlds=frozenset([WasiWorld.CLI_COMMAND]),
        ),
    )


def test_toml_expectation_filter_skips_listed_test(tmp_path: Path) -> None:
    expectations = tmp_path / "expectations.toml"
    expectations.write_text(
        """
        version = 1

        [[suite]]
        name = "WASI Rust tests [wasm32-wasip3]"

        [[suite.test]]
        name = "test-name"
        action = "skip"
        """,
        encoding="utf-8",
    )

    assert ExpectationFilter(str(expectations)).should_skip(_meta(), "test-name", Config()) == (
        True,
        "Skipped by expectation file",
    )


def test_toml_expectation_filter_does_not_skip_unlisted_test(tmp_path: Path) -> None:
    expectations = tmp_path / "expectations.toml"
    expectations.write_text(
        """
        [[suite]]
        name = "WASI Rust tests [wasm32-wasip3]"

        [[suite.test]]
        name = "other-test"
        action = "skip"
        """,
        encoding="utf-8",
    )

    assert ExpectationFilter(str(expectations)).should_skip(_meta(), "test-name", Config()) == (False, None)
