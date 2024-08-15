import os
import os.path
import pathlib
import tempfile


import click
import click.exceptions


import selenium_page_stubber.client.lib
import selenium_page_stubber.user


def check_directory_permissions(
        pages_dir: pathlib.Path = pathlib.Path("pages"),
        templates_dir: pathlib.Path = pathlib.Path("templates")) -> None:
    for directory in (pages_dir, templates_dir):
        # Check if the directory is executable by cd'ing into it
        current = os.getcwd()
        os.chdir(str(directory))
        os.chdir(current)

        # Check if the directory is readable by listing its contents
        list(directory.iterdir())

        # Check if the directory is writable by creating a temporary file
        with tempfile.TemporaryFile(dir=str(directory.resolve())):
            pass


def check_file_permissions(
        base_page_module_file: pathlib.Path = pathlib.Path("pages/Page.py"),
        base_template_file: pathlib.Path = pathlib.Path("templates/Page.jinja")) -> None:  # noqa: E501
    for file in (base_page_module_file, base_template_file):
        # Check if the file is readable by reading it
        file.read_text()

        # Check if the file is writable by opening it in write mode
        with file.open(mode="w"):
            pass


def check_permissions(
        pages_dir: pathlib.Path = pathlib.Path("pages"),
        templates_dir: pathlib.Path = pathlib.Path("templates"),
        base_page_module_file: pathlib.Path = pathlib.Path("Page.py"),
        base_template_file: pathlib.Path = pathlib.Path("Page.jinja")) -> None:
    check_directory_permissions(
        pages_dir=pages_dir,
        templates_dir=templates_dir)
    check_file_permissions(
        base_page_module_file=pages_dir / base_page_module_file,
        base_template_file=templates_dir / base_template_file)


def main(
        site: str,
        page_directory: pathlib.Path,
        template_directory: pathlib.Path,
        template_name: str,
        page_class: str,
        page_module: str) -> None:
    driver = selenium_page_stubber.client.lib.get_driver(site)
    new_page_class = selenium_page_stubber.client.lib.get_page_class(
        page_directory=page_directory,
        page_module=page_module,
        page_class=page_class,
        template_directory=template_directory,
        template_name=template_name)
    page = new_page_class(driver=driver, url=site)  # noqa: F841


@click.command
@click.option(
    "initialize", "--initialize", is_flag=True,
    envvar="INITIALIZE",
    help="Initialize pages and templates directory before creating pages")
@click.argument("site")
@click.pass_context
def cli(ctx: click.Context,
        initialize: bool,
        site: str) -> None:
    """Create the stub Selenium page."""
    pages_dir = pathlib.Path("pages")
    base_page_name = "Page"
    base_page_module_name = "Page"
    templates_dir = pathlib.Path("templates")
    base_template_file = "{}.jinja".format(base_page_module_name)
    if initialize:
        user_dir = pathlib.Path(
            os.path.split(selenium_page_stubber.user.__file__)[0])
        selenium_page_stubber.client.lib.initialize(
            pages_src=user_dir / pages_dir,
            pages_target=pages_dir,
            templates_src=user_dir / templates_dir,
            templates_target=templates_dir)

    try:
        check_permissions()
    except Exception as exc:
        click.echo(str(exc))
        raise

    main(
        site,
        pages_dir,
        templates_dir,
        base_template_file,
        base_page_name,
        base_page_module_name)
