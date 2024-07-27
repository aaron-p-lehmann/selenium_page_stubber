import logging
import pathlib
import unittest.mock


import jinja2
import pytest
import requests


import selenium_page_stubber.cli
import selenium_page_stubber.pages.Page


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


def test_get_page_class_base_class_on_parent(
        tmp_path: pathlib.Path) -> None:
    class TestParent:
        pass

    page_directory = tmp_path
    page_module = "module"
    page_class = "TestPage"
    template_directory = tmp_path
    parent = TestParent

    new_page_class = selenium_page_stubber.cli.get_page_class(
        page_directory=page_directory,
        page_module=page_module,
        page_class=page_class,
        template_directory=template_directory,
        parent=parent)
    assert new_page_class.__name__ == page_class
    assert issubclass(new_page_class, TestParent)


def test_get_page_class_from_module(tmp_path: pathlib.Path) -> None:
    page_directory = tmp_path
    page_module = "module"
    page_class = "TestPage"
    template_directory = pathlib.Path("template_directory")

    module_text = "\n".join([
        "import selenium_page_stubber.pages.Page",
        "",
        "",
        f"class {page_class}(selenium_page_stubber.pages.Page.Page):",
        "    pass"])
    with (page_directory / "{}.py".format(page_module)).open("w") as module:
        module.write(module_text)

    new_page_class = selenium_page_stubber.cli.get_page_class(
        page_directory=page_directory,
        page_module=page_module,
        page_class=page_class,
        template_directory=template_directory)

    assert new_page_class.__name__ == page_class
    assert issubclass(new_page_class, selenium_page_stubber.pages.Page.Page)


@pytest.mark.parametrize(
    ["module_text", "error"], (
        [")", SyntaxError],
        ["5 / 0", ZeroDivisionError]
    ))
def test_get_page_class_from_module_error(
        tmp_path: pathlib.Path,
        module_text: str, error: Exception) -> None:
    page_directory = tmp_path
    page_module = "module"
    page_class = "TestPage"
    template_directory = pathlib.Path("template_directory")

    with (page_directory / "{}.py".format(page_module)).open("w") as module:
        module.write(module_text)

    with pytest.raises(error):  # type: ignore[call-overload]
        selenium_page_stubber.cli.get_page_class(
            page_directory=page_directory,
            page_module=page_module,
            page_class=page_class,
            template_directory=template_directory)


def test_get_page_class_from_template(tmp_path: pathlib.Path) -> None:
    page_directory = pathlib.Path("path_directory")
    page_module = "module"
    page_class = "TestPage"
    template_directory = tmp_path
    template_text = "\n".join([
        "import selenium_page_stubber.pages.Page",
        "",
        "",
        f"class {page_class}(selenium_page_stubber.pages.Page.Page):",
        "    pass"])

    with (template_directory / page_class).open("w") as template:
        template.write(template_text)

    new_page_class = selenium_page_stubber.cli.get_page_class(
        page_directory=page_directory,
        page_module=page_module,
        page_class=page_class,
        template_directory=template_directory)

    assert new_page_class.__name__ == page_class
    assert issubclass(new_page_class, selenium_page_stubber.pages.Page.Page)


@pytest.mark.parametrize(
    ["template_text", "error"], (
        ["{% if %}", jinja2.TemplateSyntaxError],
        ["5 / 0", ZeroDivisionError]
    ))
def test_get_page_class_from_template_error(
        tmp_path: pathlib.Path, template_text: str, error: Exception) -> None:
    page_directory = pathlib.Path("path_directory")
    page_module = "module"
    page_class = "TestPage"
    template_directory = tmp_path

    with (template_directory / page_class).open("w") as template:
        template.write(template_text)

    with pytest.raises(error):  # type: ignore[call-overload]
        selenium_page_stubber.cli.get_page_class(
            page_directory=page_directory,
            page_module=page_module,
            page_class=page_class,
            template_directory=template_directory)
