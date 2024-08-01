import logging
import pathlib
import unittest.mock


import jinja2
import pytest
import requests


import selenium_page_stubber.cli
import selenium_page_stubber.user.pages.Page
import selenium_page_stubber.client.lib


@unittest.mock.patch("selenium.webdriver.chrome.webdriver.WebDriver")
@unittest.mock.patch("requests.get")
def test_get_driver_success(
        mock_requests: unittest.mock.MagicMock,
        mock_WebDriver: unittest.mock.MagicMock) -> None:
    url = "http://www.somesite.com"
    driver = selenium_page_stubber.client.lib.get_driver(url)
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
        selenium_page_stubber.client.lib.get_driver(url)
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
    template_name = "template_name"
    parent = TestParent

    new_page_class = selenium_page_stubber.client.lib.get_page_class(
        page_directory=page_directory,
        page_module=page_module,
        page_class=page_class,
        template_directory=template_directory,
        template_name=template_name,
        parent=parent)
    assert new_page_class.__name__ == page_class
    assert issubclass(new_page_class, TestParent)


def test_get_page_class_from_module(tmp_path: pathlib.Path) -> None:
    page_directory = tmp_path
    page_module = "module"
    page_class = "TestPage"
    template_directory = pathlib.Path("template_directory")
    template_name = "template_name"

    module_text = "\n".join([
        "import selenium_page_stubber.user.pages.Page",
        "",
        "",
        f"class {page_class}(selenium_page_stubber.user.pages.Page.Page):",
        "    pass"])
    with (page_directory / "{}.py".format(page_module)).open("w") as module:
        module.write(module_text)

    new_page_class = selenium_page_stubber.client.lib.get_page_class(
        page_directory=page_directory,
        page_module=page_module,
        page_class=page_class,
        template_directory=template_directory,
        template_name=template_name)

    assert new_page_class.__name__ == page_class
    assert issubclass(
        new_page_class, selenium_page_stubber.user.pages.Page.Page)


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
    template_name = "template_name"

    with (page_directory / "{}.py".format(page_module)).open("w") as module:
        module.write(module_text)

    with pytest.raises(error):  # type: ignore[call-overload]
        selenium_page_stubber.client.lib.get_page_class(
            page_directory=page_directory,
            page_module=page_module,
            page_class=page_class,
            template_directory=template_directory,
            template_name=template_name)


def test_get_page_class_from_template(tmp_path: pathlib.Path) -> None:
    page_directory = pathlib.Path("path_directory")
    page_module = "module"
    page_class = "TestPage"
    template_directory = tmp_path
    template_name = "template_name"
    template_text = "\n".join([
        "import selenium_page_stubber.user.pages.Page",
        "",
        "",
        f"class {page_class}(selenium_page_stubber.user.pages.Page.Page):",
        "    pass"])

    with (template_directory / page_class).open("w") as template:
        template.write(template_text)

    new_page_class = selenium_page_stubber.client.lib.get_page_class(
        page_directory=page_directory,
        page_module=page_module,
        page_class=page_class,
        template_directory=template_directory,
        template_name=template_name)

    assert new_page_class.__name__ == page_class
    assert issubclass(
        new_page_class, selenium_page_stubber.user.pages.Page.Page)


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
    template_name = "template_name"

    with (template_directory / page_class).open("w") as template:
        template.write(template_text)

    with pytest.raises(error):  # type: ignore[call-overload]
        selenium_page_stubber.client.lib.get_page_class(
            page_directory=page_directory,
            page_module=page_module,
            page_class=page_class,
            template_directory=template_directory,
            template_name=template_name)


def test_copy_with_possible_suffix(tmp_path: pathlib.Path) -> None:
    # Running when the file doesn't exist creates it
    selenium_page_stubber.client.lib.copy_with_possible_suffix(
        data="New File", target=tmp_path / "target.py")
    assert (tmp_path / "target.py").read_text() == "New File"

    # Running with new data when the file already exists creates a new file
    selenium_page_stubber.client.lib.copy_with_possible_suffix(
        data="New New File", target=tmp_path / "target.py")
    assert (tmp_path / "target.py").read_text() == "New File"
    assert (tmp_path / "target.new").read_text() == "New New File"

    # You can provide a different suffix
    selenium_page_stubber.client.lib.copy_with_possible_suffix(
        data="Different Suffix",
        target=tmp_path / "target.py",
        suffix="different")
    assert (tmp_path / "target.py").read_text() == "New File"
    assert (tmp_path / "target.different").read_text() == "Different Suffix"

    # If you don't provide any new data for the file, nothing will be changed
    create_time = pathlib.Path(tmp_path / "target.py").stat().st_mtime
    selenium_page_stubber.client.lib.copy_with_possible_suffix(
        data="New File", target=tmp_path / "target.py")
    assert create_time == pathlib.Path(tmp_path / "target.py").stat().st_mtime

    # If you provide new data for a file that already has a suffixed version,
    # the suffixed version will be changed
    old_suffix_data = pathlib.Path(tmp_path / "target.new").read_text()
    selenium_page_stubber.client.lib.copy_with_possible_suffix(
        data="New New New File", target=tmp_path / "target.py")
    assert (tmp_path / "target.new").read_text() != old_suffix_data

    # If the suffix is the same as the one on the target file, a ValueError
    # is raised
    with pytest.raises(ValueError) as ve:
        target_file = tmp_path / "target.py"
        selenium_page_stubber.client.lib.copy_with_possible_suffix(
            data="New File", target=target_file, suffix=".py")
    message = f"'{target_file}' has the same suffix as the one provided: '.py'"
    assert str(ve.value) == message


@unittest.mock.patch(
    "selenium_page_stubber.client.lib.copy_with_possible_suffix")
def test_initialize(
        mock_copy_with_possible_suffix: unittest.mock.MagicMock,
        tmp_path: pathlib.Path) -> None:
    class MockablePath(pathlib.Path):
        def mkdir(self,
                  mode: int = 0o777,
                  parents: bool = False,
                  exist_ok: bool = False) -> None:
            pathlib.Path.mkdir(
                self,
                mode=mode,
                parents=parents,
                exist_ok=exist_ok)

    pages_src = tmp_path / "pages_src"
    templates_src = tmp_path / "templates_src"
    pages_target = MockablePath(tmp_path) / "pages_target"
    pages_target.mkdir = unittest.mock.MagicMock(  # type: ignore[method-assign]  # noqa: E501
        wraps=pages_target.mkdir)
    pages_target_spy = pages_target.mkdir
    templates_target = MockablePath(tmp_path) / "templates_target"
    templates_target.mkdir = unittest.mock.MagicMock(  # type: ignore[method-assign]  # noqa: E501
        wraps=templates_target.mkdir)
    templates_target_spy = templates_target.mkdir

    pages_src.mkdir()
    templates_src.mkdir()
    for f in ["a.py", "b.py", "c.py"]:
        (pages_src / f).touch()
        (pages_src / f).write_text(f)
    for f in ["d.jinja", "e.jinja", "f.jinja"]:
        (templates_src / f).touch()
        (templates_src / f).write_text(f)

    selenium_page_stubber.client.lib.initialize(
        pages_src=pages_src,
        templates_src=templates_src,
        pages_target=pages_target,
        templates_target=templates_target)

    pages_target_spy.assert_called_once_with(exist_ok=True)
    templates_target_spy.assert_called_once_with(exist_ok=True)
    mock_copy_with_possible_suffix([
        unittest.mock.call(
            (src / filename).read_text(),
            (target / filename))
        for (src, target, filenames) in (
            (pages_src, pages_target, [
                "a.py", "b.py", "c.py"]),
            (templates_src, templates_target, [
                "d.jinja", "e.jinja", "f.jinja"]))
        for filename in filenames])
