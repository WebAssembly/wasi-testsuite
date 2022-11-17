from unittest.mock import Mock, patch
import pytest
import wasi_test_runner.test_suite_location as tsl


def test_get_location_invalid_config_should_raise_error() -> None:
    with pytest.raises(ValueError):
        tsl.get_test_suite_location("non-existing-path")

    with pytest.raises(ValueError):
        tsl.get_test_suite_location("invalid-protocol://unsupported")


@patch("os.path.isdir", Mock(return_value=True))
@patch("wasi_test_runner.test_suite_location.file_system_test_suite_location")
def test_get_location_existing_path_should_return_correct_location(
    location_mock: Mock,
) -> None:
    path = "existing_path"
    location_mock.return_value = path

    assert path == tsl.get_test_suite_location(path)()

    location_mock.assert_called_once_with(path)


@patch("wasi_test_runner.test_suite_location.http_zip_test_suite_location")
def test_get_location_http_should_return_correct_location(
    location_mock: Mock,
) -> None:
    url = "http://my-url.com/test.zip"
    path = "some-path"
    location_mock.return_value = path

    assert path == tsl.get_test_suite_location(url)()

    location_mock.assert_called_once_with(url)
