import logging


import click
import requests
import selenium.webdriver.chrome.webdriver


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


@click.command()
@click.option(
    "page_module", "--page-module", type=click.Path(),
    default="./pages/basic",
    help="The path to the module where the base Page class is defined")
@click.option(
    "page_class", "--page-class", default="Page",
    help="The name of the base Page class")
@click.option(
    "template_path", "--template-path", type=click.Path(),
    default="templates",
    help="The path to the Jinja templates for building the pages.")
@click.option(
    "output_directory", "--output-directory", type=click.Path(),
    default="./pages", help="The directory to put the Pages into")
@click.argument("site")
def cli(page_module: click.Path, page_class: str,
        template_path: click.Path,
        output_directory: click.Path,
        site: str) -> None:
    """Stub out Page classes for each page in SITE."""
    get_driver(site)


if __name__ == "__main__":
    cli(auto_envvar_prefix="SPS")
