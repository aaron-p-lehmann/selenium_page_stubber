import logging
import unittest.mock


import pytest
import requests


import selenium_page_stubber.cli


@unittest.mock.patch("selenium.webdriver.chrome.webdriver.WebDriver")
@unittest.mock.patch("requests.get")
def test_get_driver_success(
        mock_requests: unittest.mock.MagicMock,
        mock_WebDriver: unittest.mock.MagicMock) -> None:
    url = "http://www.somesite.com"
    driver = selenium_page_stubber.cli.get_driver(url)
    mock_WebDriver().get.assert_called_with(url)
    mock_driver = mock_WebDriver(url)
    assert driver == mock_driver


def test_get_driver_bad_url(caplog: pytest.LogCaptureFixture) -> None:
    url = "http://www.somesite.com"
    resp = requests.Response()
    resp.status_code = requests.codes.not_found
    with (pytest.raises(requests.exceptions.HTTPError),
            unittest.mock.patch("requests.get", return_value=resp),
            caplog.at_level(logging.ERROR)):
        selenium_page_stubber.cli.get_driver(url)
        assert [msg for msg in caplog.record_tuples if msg == (
            "root", logging.ERROR,
            f"{requests.codes.not_found} status when GETting {url}")]
