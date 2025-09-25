import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import Dict, NamedTuple, List, Tuple, Any

from .test_case import Output


class RuntimeVersion(NamedTuple):
    name: str
    version: str

    def __str__(self) -> str:
        return f"{self.name} {self.version}"


class RuntimeAdapterError(Exception):
    adapter_path: str

    def __init__(self, adapter_path: str) -> None:
        self.adapter_path = adapter_path


class LegacyRuntimeAdapterError(RuntimeAdapterError):
    adapter_path: str


class UnavailableRuntimeAdapterError(RuntimeAdapterError):
    error: Exception

    def __init__(self, adapter_path: str, error: Exception) -> None:
        RuntimeAdapterError.__init__(self, adapter_path)
        self.error = error


def _assert_not_legacy_adapter(adapter_path: str) -> None:
    """
    Raise an exception if the python file at ADAPTER_PATH isn't
    loadable as a normal Python module.
    """
    argv = [sys.executable, adapter_path, "--version"]
    try:
        result = subprocess.run(argv, encoding="UTF-8", check=True,
                                capture_output=True)
    except subprocess.CalledProcessError as e:
        if 'FileNotFoundError' in e.stderr:
            # The adapter is valid Python.  Running it tries to spawn
            # the engine subprocess, but couldn't find the binary.  This
            # indicates a legacy adapter.py.
            raise LegacyRuntimeAdapterError(adapter_path) from e
        # Some other error running adapter.py; could be a legacy
        # adapter, could just be a typo.  Propagate the error.
        raise UnavailableRuntimeAdapterError(adapter_path, e) from e
    assert result.stderr == "", result.stderr
    if result.stdout:
        # Running the adapter as a subprocess succeeded and produced
        # --version output: the engine is available but the adapter is
        # legacy.
        raise LegacyRuntimeAdapterError(adapter_path)
    # Otherwise if loading the file produces no output, then we assume
    # it's a module and not legacy.


def _load_adapter_as_module(adapter_path: str) -> Any:
    path = Path(adapter_path)
    spec = importlib.util.spec_from_file_location(path.name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RuntimeAdapter:
    def __init__(self, adapter_path: str) -> None:
        _assert_not_legacy_adapter(adapter_path)
        self._adapter = _load_adapter_as_module(adapter_path)
        try:
            name = self._adapter.get_name()
            version = self._adapter.get_version()
        except subprocess.CalledProcessError as e:
            raise UnavailableRuntimeAdapterError(adapter_path, e) from e
        except FileNotFoundError as e:
            raise UnavailableRuntimeAdapterError(adapter_path, e) from e
        self._version = RuntimeVersion(name, version)

    def get_version(self) -> RuntimeVersion:
        return self._version

    def compute_argv(self, test_path: str, args: List[str],
                     env_variables: Dict[str, str],
                     dirs: List[Tuple[Path, str]]) -> List[str]:
        argv = self._adapter.compute_argv(test_path=test_path,
                                          args=args,
                                          env=env_variables,
                                          dirs=dirs)
        assert isinstance(argv, list)
        assert all(isinstance(arg, str) for arg in argv)
        return argv

    def run_test(self, argv: List[str]) -> Output:
        result = subprocess.run(argv, capture_output=True, text=True,
                                check=False)
        return Output(result.returncode, result.stdout, result.stderr)
