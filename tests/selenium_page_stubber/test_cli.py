import os
import pathlib
import unittest.mock


import click.globals
import click.testing
import pytest


import selenium_page_stubber.cli
import selenium_page_stubber.user


@unittest.mock.patch("selenium_page_stubber.client.lib.get_page_class")
@unittest.mock.patch("selenium_page_stubber.client.lib.get_driver")
def test_main(
        mock_get_driver: unittest.mock.MagicMock,
        mock_get_page_class: unittest.mock.MagicMock) -> None:
    site = "https://www.site.com"
    page_directory = pathlib.Path("page_directory")
    template_directory = pathlib.Path("template_directory")
    template_name = "template_name"
    page_class = "PageClass"
    page_module = "PageModule"

    selenium_page_stubber.cli.main(
        site=site,
        page_directory=page_directory,
        template_directory=template_directory,
        template_name=template_name,
        page_class=page_class,
        page_module=page_module)
    mock_get_driver.assert_called_once_with(site)
    mock_get_page_class.assert_called_once_with(
        page_directory=page_directory,
        page_module=page_module,
        page_class=page_class,
        template_directory=template_directory,
        template_name=template_name)
    mock_get_page_class.return_value.assert_called_once_with(
        driver=mock_get_driver.return_value,
        url=site)


@pytest.mark.parametrize("set_flag", (True, False))
@unittest.mock.patch(
    "selenium_page_stubber.client.lib.initialize",
    wraps=selenium_page_stubber.client.lib.initialize)
@unittest.mock.patch("selenium_page_stubber.cli.main")
def test_cli_initialize(
        mock_main: unittest.mock.MagicMock,
        spy_initialize: unittest.mock.MagicMock,
        set_flag: bool,
        tmp_path: pathlib.Path,
        monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that we can initialize based on environment and the flag"""
    site = "https://www.site.com"
    arguments = [site]
    runner = click.testing.CliRunner()

    if set_flag:
        arguments = ["--initialize"] + arguments
    else:
        monkeypatch.setenv("INITIALIZE", "True")

    os.chdir(str(tmp_path))
    try:
        result = runner.invoke(
            selenium_page_stubber.cli.cli, arguments)
        assert result.exit_code == 0
        spy_initialize.assert_called()
        mock_main.assert_called()
    finally:
        os.chdir("..")
        for (dirpath, dirnames, filenames) in tmp_path.walk(top_down=False):
            for entry in filenames + dirnames:
                entry_path = (dirpath / entry)
                entry_path.chmod(777)
                if entry_path.is_file():
                    entry_path.unlink()
                else:
                    entry_path.rmdir()


@unittest.mock.patch("os.chdir")
@unittest.mock.patch("tempfile.TemporaryFile")
def test_check_directory_permissions(
        mock_tempfile: unittest.mock.MagicMock,
        mock_chdir: unittest.mock.MagicMock) -> None:
    class TestPath(pathlib.Path):
        pass

    directories = {
        "pages_dir": TestPath("pages"),
        "templates_dir": TestPath("templates")
    }

    for directory, path in directories.items():
        path.iterdir = unittest.mock.MagicMock()  # type: ignore[method-assign]
        path.resolve = unittest.mock.MagicMock(return_value=path)  # type: ignore[method-assign] # noqa: E501

    selenium_page_stubber.cli.check_directory_permissions(**directories)

    for path in directories.values():
        # Execution privileges were checked
        mock_chdir.assert_any_call(str(path))

        # Read privileges were checked
        path.iterdir.assert_called()  # type: ignore[attr-defined]

        # Write privilegest were checked
        mock_tempfile.assert_any_call(dir=str(path))


def test_check_file_permissions() -> None:
    class TestPath(pathlib.Path):
        pass

    pages = {
        "base_page_module_file": TestPath("Page.py"),
        "base_template_file": TestPath("Page.jinja"),
    }

    for page, path in pages.items():
        path.read_text = unittest.mock.MagicMock()  # type: ignore[method-assign] # noqa: E501
        path.open = unittest.mock.MagicMock()  # type: ignore[method-assign]

    selenium_page_stubber.cli.check_file_permissions(**pages)

    for path in pages.values():
        # Read privileges were checked
        path.read_text.assert_called()  # type: ignore[attr-defined]

        # Write privileges were checked
        path.open.assert_any_call(mode="w")  # type: ignore[attr-defined]


@unittest.mock.patch("selenium_page_stubber.cli.check_directory_permissions")
@unittest.mock.patch("selenium_page_stubber.cli.check_file_permissions")
def test_check_permissions(
        mock_check_file_permissions: unittest.mock.MagicMock,
        mock_check_directory_permissions: unittest.mock.MagicMock) -> None:
    directories = {
        "pages_dir": pathlib.Path("pages"),
        "templates_dir": pathlib.Path("templates")
    }
    files = {
        "base_page_module_file": pathlib.Path("Page.py"),
        "base_template_file": pathlib.Path("Page.jinja")
    }
    arguments = dict(files)
    arguments.update(directories)

    selenium_page_stubber.cli.check_permissions(**arguments)
    mock_check_directory_permissions.assert_called_once_with(**directories)
    mock_check_file_permissions.assert_called_once_with(**{
        "base_page_module_file": (
            directories["pages_dir"] / files["base_page_module_file"]),
        "base_template_file": (
            directories["templates_dir"] / files["base_template_file"])})


@unittest.mock.patch(
    "selenium_page_stubber.cli.check_permissions",
    side_effect=Exception("Error"))
@unittest.mock.patch("selenium_page_stubber.cli.main")
def test_cli_failed_permissions(
        mock_main: unittest.mock.MagicMock,
        mock_check_permissions: unittest.mock.MagicMock) -> None:
    runner = click.testing.CliRunner()
    result = runner.invoke(
        selenium_page_stubber.cli.cli, ["https://www.site.com"])
    assert result.exit_code == 1
    assert result.output.strip() == "Error"
