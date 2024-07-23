import importlib
import logging
import pathlib
import types


import click
from jinja2 import Environment, FileSystemLoader
import requests
import selenium.webdriver.chrome.webdriver


import pages


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
        page_class_name: str,
        template_directory: pathlib.Path,
        parent: pages.Page | None = None) -> type:
    """Get an existing page class or create a new one."""
    resolved = page_module.resolve()
    try:
        page = getattr(importlib.machinery.SourceFileLoader(
            resolved, str(resolved / f"{page_class_name}.py")).load_module(), page_class_name)
    except FileNotFoundError:
        # There's no module file, build the class from template
        try:
            env = Environment(
                loader=FileSystemLoader(str(template_directory).resolve()))
            page = exec(env.get_template(page_class_name).render())
        except FileNotFoundError:
            # There's no template, either, base it on the class in this program
            page = types.new_class(
                page_class_name, tuple() if parent is None else (parent,))
    return page


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
    "output_directory", "--output-directory", type=click.Path(exists=True),
    default="./pages", help="The directory to put the Pages into")
@click.argument("site")
def cli(page_directory: click.Path, page_class: str,
        template_directory: click.Path,
        output_directory: click.Path,
        site: str) -> None:
    """Stub out Page classes for each page in SITE."""
    driver = get_driver(site)
    page = get_page_class(
        page_directory=page_directory,
        page_class_name=page_class,
        template_directory=template_directory)(driver, site)


if __name__ == "__main__":
    cli(auto_envvar_prefix="SPS")
