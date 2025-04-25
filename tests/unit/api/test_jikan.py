from typing import Any
from unittest.mock import MagicMock

import pytest
from requests import JSONDecodeError, RequestException
import requests.exceptions
from pytest_mock.plugin import MockerFixture

from shinbotsu_data.api.jikan import JikanApiExtractor


@pytest.fixture
def mock_logger() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_request_get(mocker: MockerFixture) -> Any:
    return mocker.patch("requests.get")


def make_mock_response(
    status: int = 200, json_response: dict[str, str] | None = None, err_msg: str = ""
) -> MagicMock:
    response = MagicMock()
    response.status_code = status
    match status:
        case 404 | 429 | 500 | 503:
            http_error = requests.exceptions.HTTPError(err_msg, response=response)
            response.raise_for_status.side_effect = http_error
        case 200:
            response.json.return_value = json_response
    return response


def test_fetch_data_success(
    jikan_api_extractor: JikanApiExtractor,
    mock_request_get: MagicMock,
    mock_time_sleep: MagicMock,
) -> None:
    endpoint = "/test/endpoint"
    response_dict = {"data": "ok"}
    params: dict[str, str | int] = {"page": 1}
    mock_response = make_mock_response(json_response=response_dict)
    mock_request_get.return_value = mock_response

    result = jikan_api_extractor.fetch_data(endpoint, params=params)

    assert result == response_dict
    mock_request_get.assert_called_once_with(
        jikan_api_extractor.base_url + endpoint,
        headers=jikan_api_extractor.headers,
        params=params,
        timeout=1,
    )
    mock_response.raise_for_status.assert_called_once_with()


def test_fetch_data_timeouts(
    jikan_api_extractor: JikanApiExtractor,
    mock_request_get: MagicMock,
    mock_time_sleep: MagicMock,
    mock_logger: MagicMock,
) -> None:
    endpoint = "/test/endpoint"
    params: dict[str, str | int] = {"page": 1}
    error_msg = "Timeout error"
    mock_request_get.side_effect = requests.exceptions.Timeout(error_msg)
    jikan_api_extractor.logger = mock_logger

    result = jikan_api_extractor.fetch_data(endpoint, params=params)

    assert result is None
    assert mock_request_get.call_count == 3
    assert mock_time_sleep.call_count == 3
    assert mock_logger.error.call_count == 4
    mock_logger.error.assert_any_call(
        f"Request to {jikan_api_extractor.base_url}{endpoint} timed out: {error_msg}"
    )
    mock_logger.error.assert_called_with(
        f"Failed to fetch data from {jikan_api_extractor.base_url}{endpoint} after 3 attempts"
    )
    assert mock_logger.warning.call_count == 2


def test_fetch_data_status_404(
    jikan_api_extractor: JikanApiExtractor,
    mock_request_get: MagicMock,
    mock_time_sleep: MagicMock,
    mock_logger: MagicMock,
) -> None:
    endpoint = "/test/endpoint"
    params: dict[str, str | int] = {"page": 1}
    error_msg = "404 error"
    mock_response = make_mock_response(
        404, {"error": "resource was not found"}, error_msg
    )
    mock_request_get.return_value = mock_response
    jikan_api_extractor.logger = mock_logger

    result = jikan_api_extractor.fetch_data(endpoint, params=params)

    assert result is None
    mock_logger.error.assert_called_with(
        f"Resource was not found for {jikan_api_extractor.base_url}{endpoint}: {error_msg}"
    )


def test_fetch_data_status_429(
    jikan_api_extractor: JikanApiExtractor,
    mock_request_get: MagicMock,
    mock_time_sleep: MagicMock,
    mock_logger: MagicMock,
) -> None:
    endpoint = "/test/endpoint"
    params: dict[str, str | int] = {"page": 1}
    error_msg = "429 error"
    mock_response = make_mock_response(429, {"error": "Rate limit reached"}, error_msg)
    mock_request_get.return_value = mock_response
    jikan_api_extractor.logger = mock_logger

    result = jikan_api_extractor.fetch_data(endpoint, params=params)

    assert result is None
    mock_logger.warning.assert_any_call(f"Rate limit reached: {error_msg}")
    mock_logger.error.assert_called_with(
        f"Failed to fetch data from {jikan_api_extractor.base_url}{endpoint} after 3 attempts"
    )
    mock_time_sleep.assert_any_call(60)
    assert mock_time_sleep.call_count == 5


def test_fetch_data_status_500(
    jikan_api_extractor: JikanApiExtractor,
    mock_request_get: MagicMock,
    mock_time_sleep: MagicMock,
    mock_logger: MagicMock,
) -> None:
    endpoint = "/test/endpoint"
    params: dict[str, str | int] = {"page": 1}
    error_msg = "500 error"
    mock_response = make_mock_response(
        500, {"error": "Internal server error"}, error_msg
    )
    mock_request_get.return_value = mock_response
    jikan_api_extractor.logger = mock_logger

    result = jikan_api_extractor.fetch_data(endpoint, params=params)

    assert result is None
    mock_logger.error.assert_any_call(f"Internal server error: {error_msg}")
    mock_logger.error.assert_called_with(
        f"Failed to fetch data from {jikan_api_extractor.base_url}{endpoint} after 3 attempts"
    )
    mock_time_sleep.assert_any_call(600)
    mock_time_sleep.assert_any_call(1200)
    assert mock_time_sleep.call_count == 5


def test_fetch_data_status_503(
    jikan_api_extractor: JikanApiExtractor,
    mock_request_get: MagicMock,
    mock_time_sleep: MagicMock,
    mock_logger: MagicMock,
) -> None:
    endpoint = "/test/endpoint"
    params: dict[str, str | int] = {"page": 1}
    error_msg = "503 error"
    mock_response = make_mock_response(503, {"error": "Service unavailable"}, error_msg)
    mock_request_get.return_value = mock_response
    jikan_api_extractor.logger = mock_logger

    result = jikan_api_extractor.fetch_data(endpoint, params=params)

    assert result is None
    mock_logger.error.assert_any_call(f"Service unavailable: {error_msg}")
    mock_logger.error.assert_called_with(
        f"Failed to fetch data from {jikan_api_extractor.base_url}{endpoint} after 3 attempts"
    )
    mock_time_sleep.assert_any_call(600)
    mock_time_sleep.assert_any_call(1200)
    assert mock_time_sleep.call_count == 5


def test_fetch_data_request_execption(
    jikan_api_extractor: JikanApiExtractor,
    mock_request_get: MagicMock,
    mock_time_sleep: MagicMock,
    mock_logger: MagicMock,
) -> None:
    endpoint = "/test/endpoint"
    params: dict[str, str | int] = {"page": 1}
    mock_response = make_mock_response()
    error_msg = "Request error"
    mock_request_get.return_value = mock_response
    mock_request_get.side_effect = RequestException(error_msg)
    jikan_api_extractor.logger = mock_logger

    result = jikan_api_extractor.fetch_data(endpoint, params=params)

    assert result is None
    mock_logger.error.assert_called_once_with(f"Other error occurred: {error_msg}")


def test_fetch_data_json_decode_error(
    jikan_api_extractor: JikanApiExtractor,
    mock_request_get: MagicMock,
    mock_time_sleep: MagicMock,
    mock_logger: MagicMock,
) -> None:
    endpoint = "/test/endpoint"
    params: dict[str, str | int] = {"page": 1}
    mock_response = make_mock_response()
    error_msg = "Json error"
    mock_request_get.return_value = mock_response
    mock_response.json.side_effect = JSONDecodeError(error_msg, '{"data": "hello"', 0)
    jikan_api_extractor.logger = mock_logger

    result = jikan_api_extractor.fetch_data(endpoint, params=params)

    assert result is None
    mock_logger.error.assert_called_once_with(
        f"Other error occurred: {error_msg}: line 1 column 1 (char 0)"
    )
