import os
import pathlib
from typing import cast
import unittest.mock


import click.testing
import pytest


import selenium_page_stubber.cli
import selenium_page_stubber.user


@unittest.mock.patch("selenium_page_stubber.client.lib.get_page_class")
@unittest.mock.patch("selenium_page_stubber.client.lib.get_driver")
def test_stub_pages_main(
        mock_get_driver: unittest.mock.MagicMock,
        mock_get_page_class: unittest.mock.MagicMock) -> None:
    site = "https://www.site.com"
    page_directory = pathlib.Path("page_directory")
    template_directory = pathlib.Path("template_directory")
    template_name = "template_name"
    output_directory = pathlib.Path("output_directory")
    page_class = "PageClass"
    page_module = "PageModule"

    selenium_page_stubber.cli.stub_pages_main(
        site=site,
        page_directory=page_directory,
        template_directory=template_directory,
        template_name=template_name,
        output_directory=output_directory,
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


@pytest.mark.parametrize(
    ["options", "expected_result", "expected_output"], (
        # Directories con't exist as files
        (["--page-directory", "file",
          "--template-directory", "directory",
          "--output-directory", "directory"], 2,
          "Invalid value for '--page-directory': Directory 'file' is a file"),  # noqa: E501
        (["--page-directory", "directory",
          "--template-directory", "file",
          "--output-directory", "directory"], 2,
          "Invalid value for '--template-directory': Directory 'file' is a file"),  # noqa: E501
        (["--page-directory", "directory",
          "--template-directory", "directory",
          "--output-directory", "file"], 2,
          "Invalid value for '--output-directory': Directory 'file' is a file"),  # noqa: E501

        # Directories have to be readable
        (["--page-directory", "non-readable",
          "--template-directory", "directory",
          "--output-directory", "directory"], 2,
          "Invalid value for '--page-directory': Directory 'non-readable' is not readable"),  # noqa: E501
        (["--page-directory", "directory",
          "--template-directory", "non-readable",
          "--output-directory", "directory"], 2,
          "Invalid value for '--template-directory': Directory 'non-readable' is not readable"),  # noqa: E501
        (["--page-directory", "directory",
          "--template-directory", "directory",
          "--output-directory", "non-readable"], 2,
          "Invalid value for '--output-directory': Directory 'non-readable' is not readable"),  # noqa: E501

        # Directories have to be executable
        (["--page-directory", "non-executable",
          "--template-directory", "directory",
          "--output-directory", "directory"], 2,
          "Invalid value for '--page-directory': Directory 'non-executable' is not executable"),  # noqa: E501
        (["--page-directory", "directory",
          "--template-directory", "non-executable",
          "--output-directory", "directory"], 2,
          "Invalid value for '--template-directory': Directory 'non-executable' is not executable"),  # noqa: E501
        (["--page-directory", "directory",
          "--template-directory", "directory",
          "--output-directory", "non-executable"], 2,
          "Invalid value for '--output-directory': Directory 'non-executable' is not executable"),  # noqa: E501

        # Output has to be writable
        (["--page-directory", "non-writable",
          "--template-directory", "directory",
          "--output-directory", "directory"], 0, ""),
        (["--page-directory", "directory",
          "--template-directory", "non-writable",
          "--output-directory", "directory"], 0, ""),
        (["--page-directory", "directory",
          "--template-directory", "directory",
          "--output-directory", "non-writable"], 2,
          "Invalid value for '--output-directory': Directory 'non-writable' is not writable"),  # noqa: E501

        # Provided a non-writable to both page and output, will fail on output
        (["--page-directory", "non-writable",
          "--template-directory", "directory",
          "--output-directory", "non-writable"], 2,
          "Invalid value for '--output-directory': Directory 'non-writable' is not writable"),  # noqa: E501
    ))
@unittest.mock.patch("selenium_page_stubber.cli.stub_pages_main")
def test_cli_paths(
        mock_stub_pages_main: unittest.mock.MagicMock,
        options: list[str],
        expected_result: int,
        expected_output: str,
        tmp_path: pathlib.Path) -> None:
    """Verify the directory options do the appropriate checks."""
    # Create file structure
    directories = dict(
        (name, tmp_path / name)
        for name in [
            "directory", "non-readable", "non-writable", "non-executable"])
    for directory in directories.values():
        directory.mkdir()
        (directory / "Page.py").touch()
        (directory / "Page.jinja").touch()
    directories["non-readable"].chmod(0o300)
    directories["non-executable"].chmod(0o600)
    directories["non-writable"].chmod(0o500)
    (tmp_path / "file").touch()
    os.chdir(str(tmp_path.resolve()))

    try:
        # Test variables
        site = "https://www.site.com"
        runner = click.testing.CliRunner()

        runner_args = options[:4] + ["stub-pages"] + options[4:] + [site]
        result = runner.invoke(
            selenium_page_stubber.cli.cli,
            runner_args)
        assert result.exit_code == expected_result
        assert expected_output in result.output
        if expected_result == 0:
            # The command succeeded and was supposed to,
            # verify the right stuff was passed to main()
            arguments: dict[str, str | pathlib.Path] = {
                "site": site,
                "page_module": "Page",
                "page_class": "Page",
                "template_name": "Page.jinja"
            }
            update_args = dict(
                (option[2:].replace("-", "_"), pathlib.Path(value))
                for (option, value) in zip(
                    options[0:len(options):2], options[1:len(options):2]))
            arguments.update(update_args)
            mock_stub_pages_main.assert_called_once_with(**arguments)
    finally:
        os.chdir("..")
        (tmp_path / "file").chmod(0o777)
        (tmp_path / "directory").chmod(0o777)
        (tmp_path / "non-readable").chmod(0o777)
        (tmp_path / "non-writable").chmod(0o777)
        (tmp_path / "non-executable").chmod(0o777)


@unittest.mock.patch("selenium_page_stubber.cli.stub_pages_main")
@unittest.mock.patch("pathlib.Path.read_text")
def test_output_directory_and_template_name(
        mock_read_text: unittest.mock.MagicMock,
        mock_stub_pages_main: unittest.mock.MagicMock,
        tmp_path: pathlib.Path) -> None:
    """Verify that output_directory is the same as the page_directory if it
    isn't supplied.
    """
    inputs: dict[str, str | pathlib.Path] = {
        "site": "site",
        "page_directory": pathlib.Path("pages"),
        "template_directory": pathlib.Path("templates"),
        "page_class": "Page",
        "page_module": "Page"
    }
    os.chdir(str(tmp_path.resolve()))
    cast(pathlib.Path, inputs["page_directory"]).mkdir()
    cast(pathlib.Path, inputs["template_directory"]).mkdir()
    pathlib.Path("other_page_directory").mkdir()
    runner = click.testing.CliRunner()

    # If we pass in defaults, output_directory will be "pages" and
    # template_name will be Page.jinja
    runner.invoke(selenium_page_stubber.cli.cli, ["stub-pages", "site"])
    defaults = {
        "output_directory": inputs["page_directory"],
        "template_name": "{}.jinja".format(inputs["page_module"])}
    defaults.update(inputs)
    mock_stub_pages_main.assert_called_once_with(**defaults)
    mock_stub_pages_main.reset_mock()

    # If we pass in a value for page_directory and page_module and none for
    # output_directory or template_name, output_directory will match
    # page_directory and template_name will be <page_module>.jinja
    modified_page_stuff = dict(inputs)
    modified_page_stuff.update({
        "page_directory": pathlib.Path("other_page_directory"),
        "page_module": "other_page_module",
        "output_directory": pathlib.Path("other_page_directory"),
        "template_name": "other_page_module.jinja"})
    runner.invoke(selenium_page_stubber.cli.cli, [
        "--page-directory", str(modified_page_stuff["page_directory"]),
        "--page-module", "other_page_module",
        "stub-pages", "site"])
    mock_stub_pages_main.assert_called_once_with(**modified_page_stuff)
    mock_stub_pages_main.reset_mock()

    # If we pass in a value for output_directory and template_name
    # output_directory and template_name will match what we pass in
    temporary_directory = cast(pathlib.Path, inputs["template_directory"])
    (temporary_directory / "template_name.jinja").touch()
    new_values = dict(inputs)
    new_values.update({
        "output_directory": pathlib.Path("new_output_directory"),
        "template_name": "template_name.jinja"})
    runner.invoke(selenium_page_stubber.cli.cli, [
        "--template-name", str(new_values["template_name"]),
        "stub-pages",
        "--output-directory", str(new_values["output_directory"]),
        "site"])
    mock_stub_pages_main.assert_called_once_with(**new_values)


@unittest.mock.patch("selenium_page_stubber.cli.stub_pages_main")
def test_module_path_checking(
        mock_stub_pages_main: unittest.mock.MagicMock,
        tmp_path: pathlib.Path) -> None:
    """Verify the base page module checking."""
    site = "https://www.site.com"
    page_directory = "pages"
    template_directory = "templates"
    template_name = "template_name.jinja"
    output_directory = page_directory
    page_module = "Page"
    page_class = "Page"
    module_path = (
        tmp_path / page_directory / "{}.py".format(page_module)).resolve()
    template_path = (
        tmp_path / template_directory / template_name).resolve()
    (tmp_path / page_directory).mkdir()
    (tmp_path / template_directory).mkdir()
    template_path.touch()

    os.chdir(str(tmp_path.resolve()))
    runner = click.testing.CliRunner()

    # If the module doesn't exist
    result = runner.invoke(
        selenium_page_stubber.cli.cli,
        ["--page-directory", page_directory,
         "--page-class", page_class,
         "--page-module", page_module,
         "--template-directory", template_directory,
         "--template-name", template_name,
         "stub-pages", "--output-directory", output_directory, site])
    assert result.exit_code == 2
    assert "'pages/Page.py' does not exist" in result.output

    # If the module exists, but isn't readable
    module_path.touch(mode=0o300)
    try:
        result = runner.invoke(
            selenium_page_stubber.cli.cli,
            ["--page-directory", page_directory,
             "--page-class", page_class,
             "--page-module", page_module,
             "--template-directory", template_directory,
             "--template-name", template_name,
             "stub-pages", "--output-directory", output_directory, site])
        assert result.exit_code == 2
        assert "'pages/Page.py' is not readable" in result.output
    finally:
        module_path.chmod(0o777)

    # If the module exists and is readable
    result = runner.invoke(
        selenium_page_stubber.cli.cli,
        ["--page-directory", page_directory,
         "--page-class", page_class,
         "--page-module", page_module,
         "--template-directory", template_directory,
         "--template-name", template_name,
         "stub-pages", "--output-directory", output_directory, site])
    assert result.exit_code == 0
    mock_stub_pages_main.assert_called()


@unittest.mock.patch("selenium_page_stubber.cli.stub_pages_main")
def test_template_path_checking(
        mock_stub_pages_main: unittest.mock.MagicMock,
        tmp_path: pathlib.Path) -> None:
    """Verify the base page module checking."""
    site = "https://www.site.com"
    page_directory = "pages"
    template_directory = "templates"
    template_name = "template_name.jinja"
    output_directory = page_directory
    page_module = "Page"
    page_class = "Page"
    module_path = (
        tmp_path / page_directory / "{}.py".format(page_module)).resolve()
    template_path = (
        tmp_path / template_directory / template_name).resolve()
    (tmp_path / page_directory).mkdir()
    (tmp_path / template_directory).mkdir()
    module_path.touch()

    os.chdir(str(tmp_path.resolve()))
    runner = click.testing.CliRunner()

    # If the template doesn't exist
    result = runner.invoke(
        selenium_page_stubber.cli.cli,
        ["--page-directory", page_directory,
         "--page-class", page_class,
         "--page-module", page_module,
         "--template-directory", template_directory,
         "--template-name", template_name,
         "stub-pages", "--output-directory", output_directory, site])
    assert result.exit_code == 2
    assert "'templates/template_name.jinja' does not exist" in result.output

    # If the template exists, but isn't readable
    template_path.touch(mode=0o300)
    try:
        result = runner.invoke(
            selenium_page_stubber.cli.cli,
            ["--page-directory", page_directory,
             "--page-class", page_class,
             "--page-module", page_module,
             "--template-directory", template_directory,
             "--template-name", template_name,
             "stub-pages", "--output-directory", output_directory, site])
        assert result.exit_code == 2
        assert "'templates/template_name.jinja' is not readable" in result.output  # noqa: E501
    finally:
        template_path.chmod(0o777)

    # If the module exists and is readable
    result = runner.invoke(
        selenium_page_stubber.cli.cli,
        ["--page-directory", page_directory,
         "--page-class", page_class,
         "--page-module", page_module,
         "--template-directory", template_directory,
         "--template-name", template_name,
         "stub-pages", "--output-directory", output_directory, site])
    assert result.exit_code == 0
    mock_stub_pages_main.assert_called()


@unittest.mock.patch("pathlib.Path.read_text")
@unittest.mock.patch("selenium_page_stubber.cli.stub_pages_main")
def test_environment_variables(
        mock_stub_pages_main: unittest.mock.MagicMock,
        mock_read_text: unittest.mock.MagicMock,
        tmp_path: pathlib.Path,
        monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that we can get the options from environment variables"""
    page_module = "page_module"
    page_class = "page_class"
    template_name = "template_name"
    site = "https://www.site.com"
    tmp_path_resolved = tmp_path.resolve()
    monkeypatch.setenv("SPS_PAGE_DIRECTORY", str(tmp_path_resolved))
    monkeypatch.setenv("SPS_PAGE_MODULE", page_module)
    monkeypatch.setenv("SPS_PAGE_CLASS", page_class)
    monkeypatch.setenv("SPS_TEMPLATE_DIRECTORY", str(tmp_path_resolved))
    monkeypatch.setenv("SPS_TEMPLATE_NAME", template_name)
    monkeypatch.setenv("SPS_OUTPUT_DIRECTORY", str(tmp_path_resolved))
    runner = click.testing.CliRunner()

    result = runner.invoke(selenium_page_stubber.cli.cli, ["stub-pages", site])
    assert result.exit_code == 0
    mock_stub_pages_main.assert_called_with(**{
        "page_directory": tmp_path_resolved,
        "page_module": page_module,
        "page_class": page_class,
        "template_directory": tmp_path_resolved,
        "template_name": template_name,
        "output_directory": tmp_path_resolved,
        "site": site})


@unittest.mock.patch("pathlib.Path.read_text")
@unittest.mock.patch("selenium_page_stubber.client.lib.initialize")
def test_initialize(
        mock_initialize: unittest.mock.MagicMock,
        mock_read_text: unittest.mock.MagicMock,
        tmp_path: pathlib.Path) -> None:
    """Verify initialize subcommand cli works"""
    page_module = "page_module"
    page_class = "page_class"
    template_name = "template_name"
    tmp_path_resolved = tmp_path.resolve()
    user_dir = pathlib.Path(
        os.path.split(selenium_page_stubber.user.__file__)[0])
    runner = click.testing.CliRunner()

    result = runner.invoke(
        selenium_page_stubber.cli.cli,
        ["--page-directory", str(tmp_path_resolved / "pages"),
         "--page-module", page_module,
         "--page-class", page_class,
         "--template-name", template_name,
         "--template-directory", str(
             tmp_path_resolved / "templates"), "initialize"])
    assert result.exit_code == 0
    mock_initialize.assert_called_with(**{
        "pages_src": user_dir / "pages",
        "pages_target": tmp_path / "pages",
        "templates_src": user_dir / "templates",
        "templates_target": tmp_path / "templates"})
