import os.path
import pathlib


import click
import click.exceptions


import selenium_page_stubber.client.lib
import selenium_page_stubber.user


def stub_pages_main(
        site: str,
        page_directory: pathlib.Path,
        template_directory: pathlib.Path,
        template_name: str,
        output_directory: pathlib.Path,
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


@click.group(context_settings={"auto_envvar_prefix": "SPS"})
@click.option(
    "page_directory", "--page-directory", default="pages",
    type=click.Path(
        path_type=pathlib.Path, file_okay=False,
        readable=True, executable=True),
    help="The path to the directory where the Page modules are")
@click.option(
    "page_module", "--page-module", default="Page",
    help="The module the base page class is in")
@click.option(
    "page_class", "--page-class", default="Page",
    help="The name of the base Page class")
@click.option(
    "template_directory", "--template-directory",
    type=click.Path(
        path_type=pathlib.Path, file_okay=False,
        readable=True, executable=True),
    default="templates",
    help="The path to the Jinja apps for building the pages.")
@click.option(
    "template_name", "--template-name",
    help=("The name of the jinja template for building pages.  "
          "Defaults to <page_module>.jinja"))
@click.pass_context
def cli(ctx: click.Context,
        page_directory: pathlib.Path,
        page_module: str,
        page_class: str,
        template_directory: pathlib.Path,
        template_name: str | None) -> None:
    """Stub out Page classes for each page in SITE."""
    ctx.ensure_object(dict)

    template_name = template_name if template_name else f"{page_module}.jinja"
    ctx.obj.update({
        "page_directory": page_directory,
        "page_module": page_module,
        "page_class": page_class,
        "template_directory": template_directory,
        "template_name": template_name})


@cli.command()
@click.option(
    "output_directory", "--output-directory",
    type=click.Path(
        path_type=pathlib.Path, file_okay=False, readable=True,
        executable=True, writable=True),
    default="",
    help=("The directory where the output files will be placed.  "
          "Defaults to <page_directory>"))
@click.argument("site")
@click.pass_context
def stub_pages(
        ctx: click.Context,
        output_directory: pathlib.Path,
        site: str) -> None:
    """Create the stub Selenium pages."""
    ctx.ensure_object(dict)
    ctx.obj["output_directory"] = (
        ctx.obj["page_directory"]
        if output_directory == pathlib.Path("")
        else output_directory)

    page_directory = ctx.obj["page_directory"]
    page_module = ctx.obj["page_module"]
    template_directory = ctx.obj["template_directory"]
    template_name = ctx.obj["template_name"]

    # verify base page module is readable
    page_module_file = page_directory / "{}.py".format(
        page_module)
    try:
        page_module_file.read_text()
    except PermissionError:
        click.echo(f"'{page_module_file}' is not readable", err=True)
        ctx.exit(2)
    except FileNotFoundError:
        click.echo(f"'{page_module_file}' does not exist", err=True)
        ctx.exit(2)

    # verify the base template is readable
    template_file = template_directory / template_name
    try:
        template_file.read_text()
    except PermissionError:
        click.echo(f"'{template_file}' is not readable", err=True)
        ctx.exit(2)
    except FileNotFoundError:
        click.echo(f"'{template_file}' does not exist", err=True)
        ctx.exit(2)
    ctx.obj['site'] = site
    stub_pages_main(**ctx.obj)


@cli.command()
@click.pass_context
def initialize(ctx: click.Context) -> None:
    """Initialize the page and template directories"""
    user_dir = pathlib.Path(
        os.path.split(selenium_page_stubber.user.__file__)[0])
    selenium_page_stubber.client.lib.initialize(
        pages_src=user_dir / "pages",
        pages_target=ctx.obj["page_directory"],
        templates_src=user_dir / "templates",
        templates_target=ctx.obj["template_directory"])
