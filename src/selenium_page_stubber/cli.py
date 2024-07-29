import pathlib


import click


import selenium_page_stubber.client.lib


def main(
        site: str,
        page_directory: pathlib.Path,
        template_directory: pathlib.Path,
        output_directory: pathlib.Path,
        page_class: str,
        page_module: str) -> None:
    driver = selenium_page_stubber.client.lib.get_driver(site)
    new_page_class = selenium_page_stubber.client.lib.get_page_class(
        page_directory=page_directory,
        page_module=page_module,
        page_class=page_class,
        template_directory=template_directory)
    page = new_page_class(driver=driver, url=site)  # noqa: F841


@click.command(context_settings={"auto_envvar_prefix": "SPS"})
@click.option(
    "page_directory", "--page-directory", default="pages",
    type=click.Path(
        exists=True, path_type=pathlib.Path, file_okay=False,
        readable=True, executable=True),
    help="The path to the directory where the Page modules are")
@click.option(
    "page_class", "--page-class", default="Page",
    help="The name of the base Page class")
@click.option(
    "template_directory", "--template-directory",
    type=click.Path(
        exists=True, path_type=pathlib.Path, file_okay=False,
        readable=True, executable=True),
    default="templates",
    help="The path to the Jinja apps for building the pages.")
@click.option(
    "output_directory", "--output-directory",
    type=click.Path(
        exists=False, path_type=pathlib.Path, file_okay=False,
        readable=True, writable=True, executable=True),
    default="pages", help="The directory to put the Pages into")
@click.option(
    "page_module", "--page-module", default="Page",
    help="The module the base page class is in")
@click.argument("site")
@click.pass_context
def cli(ctx: click.Context,
        page_directory: pathlib.Path,
        page_class: str,
        template_directory: pathlib.Path,
        output_directory: pathlib.Path,
        page_module: str,
        site: str) -> None:
    """Stub out Page classes for each page in SITE."""
    page_module_file = page_directory / "{}.py".format(page_module)
    try:
        page_module_file.read_text()
    except PermissionError:
        click.echo(f"'{page_module_file}' is not readable", err=True)
        ctx.exit(2)
    except FileNotFoundError:
        click.echo(f"'{page_module_file}' does not exist", err=True)
        ctx.exit(2)

    main(page_directory=page_directory,
         page_class=page_class,
         template_directory=template_directory,
         output_directory=output_directory,
         page_module=page_module,
         site=site)
