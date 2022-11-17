import os

from hashlib import sha1
from io import BytesIO
from typing import Callable
from urllib.parse import urlparse
from urllib.request import urlopen
from zipfile import ZipFile


TestSuiteLocation = Callable[[], str]


def file_system_test_suite_location(path: str) -> str:
    return path


def http_zip_test_suite_location(url: str) -> str:
    dirname = f"wasi-tests-{sha1(url.encode(encoding='UTF-8')).hexdigest()[:7]}"
    extract_path = os.path.join("_test_cache", dirname)

    if not os.path.exists(extract_path):
        with ZipFile(BytesIO(urlopen(url).read())) as zip_file:
            zip_file.extractall(extract_path)

    subdirs = list(
        filter(
            os.path.isdir,
            map(lambda p: os.path.join(extract_path, p), os.listdir(extract_path)),
        )
    )

    if len(subdirs) != 1:
        raise RuntimeError(
            f"Expected a single directory in a zip archive, have: {subdirs}"
        )

    return subdirs[0]


def get_test_suite_location(config: str) -> TestSuiteLocation:
    if os.path.isdir(config):
        return lambda: file_system_test_suite_location(config)

    if _is_http_url(config):
        return lambda: http_zip_test_suite_location(config)

    raise ValueError(f"Unsupported configuration string {config}")


def _is_http_url(path: str) -> bool:
    ret = urlparse(path)
    return ret.scheme in ["http", "https"] and len(ret.netloc) > 0
