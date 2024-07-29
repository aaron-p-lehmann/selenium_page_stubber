import os
import pathlib
import unittest.mock


import click.testing
import pytest


import selenium_page_stubber.cli


@unittest.mock.patch("selenium_page_stubber.client.lib.get_page_class")
@unittest.mock.patch("selenium_page_stubber.client.lib.get_driver")
def test_main(
        mock_get_driver: unittest.mock.MagicMock,
        mock_get_page_class: unittest.mock.MagicMock) -> None:
    site = "https://www.site.com"
    page_directory = pathlib.Path("page_directory")
    template_directory = pathlib.Path("template_directory")
    output_directory = pathlib.Path("output_directory")
    page_class = "PageClass"
    page_module = "PageModule"

    selenium_page_stubber.cli.main(
        site,
        page_directory,
        template_directory,
        output_directory,
        page_class,
        page_module)
    mock_get_driver.assert_called_once_with(site)
    mock_get_page_class.assert_called_once_with(
        page_directory=page_directory,
        page_module=page_module,
        page_class=page_class,
        template_directory=template_directory)
    mock_get_page_class.return_value.assert_called_once_with(
        driver=mock_get_driver.return_value,
        url=site)


@pytest.mark.parametrize(
    ["options", "expected_result", "expected_output"], (
        # Non-existent directories
        (["--page-directory", "non-existent",
          "--template-directory", "directory",
          "--output-directory", "directory"], 2,
          "Invalid value for '--page-directory': Directory 'non-existent' does not exist"),  # noqa: E501
        (["--page-directory", "directory",
          "--template-directory", "non-existent",
          "--output-directory", "directory"], 2,
          "Invalid value for '--template-directory': Directory 'non-existent' does not exist"),  # noqa: E501
        (["--page-directory", "directory",
          "--template-directory", "directory",
          "--output-directory", "non-existent"], 0, ""),

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
@unittest.mock.patch("pathlib.Path.read_text")
@unittest.mock.patch("selenium_page_stubber.cli.main")
def test_cli_paths(
        mock_main: unittest.mock.MagicMock,
        mock_read_text: unittest.mock.MagicMock,
        options: list[str],
        expected_result: int,
        expected_output: str,
        tmp_path: pathlib.Path) -> None:
    """Verify the directory options do the appropriate checks."""
    # Create file structure
    (tmp_path / "directory").mkdir(mode=0o700)
    (tmp_path / "non-readable").mkdir(mode=0o300)
    (tmp_path / "non-writable").mkdir(mode=0o500)
    (tmp_path / "non-executable").mkdir(mode=0o600)
    (tmp_path / "file").touch()
    os.chdir(str(tmp_path.resolve()))

    try:
        # Test variables
        site = "https://www.site.com"
        runner = click.testing.CliRunner()

        result = runner.invoke(selenium_page_stubber.cli.cli, [site] + options)
        assert result.exit_code == expected_result
        assert expected_output in result.output
        if expected_result == 0:
            # The command succeeded and was supposed to,
            # verify the right stuff was passed to main()
            arguments: dict[str, str | pathlib.Path] = {
                "site": site,
                "page_module": "Page",
                "page_class": "Page"
            }
            arguments.update(dict(
                (option[2:].replace("-", "_"), pathlib.Path(value))
                for (option, value) in zip(
                    options[0:len(options):2], options[1:len(options):2])))
            mock_main.assert_called_once_with(**arguments)
    finally:
        os.chdir("..")
        (tmp_path / "file").chmod(0o777)
        (tmp_path / "directory").chmod(0o777)
        (tmp_path / "non-readable").chmod(0o777)
        (tmp_path / "non-writable").chmod(0o777)
        (tmp_path / "non-executable").chmod(0o777)


@unittest.mock.patch("selenium_page_stubber.cli.main")
def test_module_path_checking(
        mock_main: unittest.mock.MagicMock,
        tmp_path: pathlib.Path) -> None:
    """Verify the base page module checking."""
    site = "https://www.site.com"
    page_directory = "pages"
    template_directory = "templates"
    output_directory = page_directory
    page_module = "Page"
    page_class = "Page"
    module_path = (
        tmp_path / page_directory / "{}.py".format(page_module)).resolve()
    (tmp_path / page_directory).mkdir()
    (tmp_path / template_directory).mkdir()
    os.chdir(str(tmp_path.resolve()))
    runner = click.testing.CliRunner()

    # If the module doesn't exist
    result = runner.invoke(
        selenium_page_stubber.cli.cli,
        ["--page-directory", page_directory,
         "--template-directory", template_directory,
         "--output-directory", output_directory,
         "--page-class", page_class,
         "--page-module", page_module, site])
    assert result.exit_code == 2
    assert "'pages/Page.py' does not exist" in result.output

    # If the module exists, but isn't readable
    module_path.touch(mode=0o300)
    try:
        result = runner.invoke(
            selenium_page_stubber.cli.cli,
            ["--page-directory", page_directory,
             "--template-directory", template_directory,
             "--output-directory", output_directory,
             "--page-class", page_class,
             "--page-module", page_module, site])
        assert result.exit_code == 2
        assert "'pages/Page.py' is not readable" in result.output
    finally:
        module_path.chmod(0o777)

    # If the module exists and is readable
    result = runner.invoke(
        selenium_page_stubber.cli.cli,
        ["--page-directory", page_directory,
         "--template-directory", template_directory,
         "--output-directory", output_directory,
         "--page-class", page_class,
         "--page-module", page_module, site])
    assert result.exit_code == 0
    mock_main.assert_called()


@unittest.mock.patch("pathlib.Path.read_text")
@unittest.mock.patch("selenium_page_stubber.cli.main")
def test_environment_variables(
        mock_main: unittest.mock.MagicMock,
        mock_read_text: unittest.mock.MagicMock,
        tmp_path: pathlib.Path,
        monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that we can get the options from environment variables"""
    page_module = "page_module"
    page_class = "page_class"
    site = "https://www.site.com"
    tmp_path_resolved = tmp_path.resolve()
    monkeypatch.setenv("SPS_PAGE_DIRECTORY", str(tmp_path_resolved))
    monkeypatch.setenv("SPS_TEMPLATE_DIRECTORY", str(tmp_path_resolved))
    monkeypatch.setenv("SPS_OUTPUT_DIRECTORY", str(tmp_path_resolved))
    monkeypatch.setenv("SPS_PAGE_MODULE", page_module)
    monkeypatch.setenv("SPS_PAGE_CLASS", page_class)
    runner = click.testing.CliRunner()

    result = runner.invoke(selenium_page_stubber.cli.cli, [site])
    assert result.exit_code == 0
    mock_main.assert_called_with(**{
        "site": site,
        "page_directory": tmp_path_resolved,
        "template_directory": tmp_path_resolved,
        "output_directory": tmp_path_resolved,
        "page_module": page_module,
        "page_class": page_class})
