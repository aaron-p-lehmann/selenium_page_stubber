import importlib
import logging
import pathlib
import types
from typing import cast


import click
from jinja2 import Environment, FileSystemLoader
import requests
import selenium.webdriver.chrome.webdriver


import selenium_page_stubber.pages.Page


def get_driver(site: str) -> selenium.webdriver.chrome.webdriver.WebDriver:
    """Get a WebDriver pointed at the site, or raise HTTPError."""
    try:
        resp = requests.get(site)
        resp.raise_for_status()
    except requests.HTTPError:
        logging.error("%d status when GETting %s", resp.status_code, site)
        raise
    driver = selenium.webdriver.chrome.webdriver.WebDriver()
    driver.get(site)
    return driver


def get_page_class(
        page_directory: pathlib.Path,
        page_module: str,
        page_class: str,
        template_directory: pathlib.Path,
        parent: type = selenium_page_stubber.pages.Page.Page) -> type:
    """Get an existing page class or create a new one."""
    try:
        module_file = "{}.py".format(page_module)
        return cast(type, getattr(importlib.machinery.SourceFileLoader(
            page_module,
            str((page_directory / module_file).resolve())).load_module(),
            page_class))
    except FileNotFoundError:
        # There's no module file, build the class from template
        try:
            env = Environment(
                loader=FileSystemLoader(str(template_directory.resolve())))
            return cast(type, eval(env.get_template(page_class).render()))
        except FileNotFoundError:
            # There's no template, either, base it on the parent class
            return types.new_class(page_class, (parent,))


@click.command()
@click.option(
    "page_directory", "--page-directory", default="./pages",
    type=click.Path(exists=True, path_type=pathlib.Path),
    help="The path to the directory where the Page modules are")
@click.option(
    "page_class", "--page-class", default="Page",
    help="The name of the base Page class")
@click.option(
    "template_directory", "--template-directory",
    type=click.Path(exists=True, path_type=pathlib.Path),
    default="templates",
    help="The path to the Jinja apps for building the pages.")
@click.option(
    "output_directory", "--output-directory",
    type=click.Path(exists=True, path_type=pathlib.Path),
    default="./pages", help="The directory to put the Pages into")
@click.option(
    "page_module", "--page-module", default="Page",
    help="The module the base page class is in")
@click.argument("site")
def cli(page_directory: pathlib.Path,
        page_class: str,
        template_directory: pathlib.Path,
        output_directory: pathlib.Path,
        page_module: str,
        site: str) -> None:
    """Stub out Page classes for each page in SITE."""
    driver = get_driver(site)
    page = get_page_class(  # noqa: F841
        page_directory=page_directory,
        page_module=page_module,
        page_class=page_class,
        template_directory=template_directory)(driver, site)


if __name__ == "__main__":
    cli(auto_envvar_prefix="SPS")
