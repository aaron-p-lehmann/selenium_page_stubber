import importlib
import importlib.abc
import logging
import pathlib
import types
from typing import cast


import jinja2
import requests
import selenium.webdriver.chrome.webdriver
import selenium.webdriver.common.by
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
    module_file = "{}.py".format(page_module)
    module_path = (page_directory / module_file).resolve()
    template_path = template_directory.resolve()
    new_class = parent
    if module_path.is_file():
        # Get the class from a module local to the project
        spec = importlib.util.spec_from_file_location(
            page_module, str(module_path))
        if isinstance(spec, importlib.machinery.ModuleSpec) and isinstance(spec.loader, importlib.abc.Loader):  # noqa: E501
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            new_class = cast(type, getattr(module, page_class))
    elif (template_path / page_class).resolve().is_file():
        # Get the class described in the template
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_path))
        module_source = env.get_template(page_class).render()
        spec = importlib.util.spec_from_loader(page_module, loader=None)
        if isinstance(spec, importlib.machinery.ModuleSpec):
            module = importlib.util.module_from_spec(spec)
            exec(module_source, module.__dict__)
            new_class = cast(type, getattr(module, page_class))
    else:
        # Neither a module nor a template exists for the page class we need,
        # create one based on parent
        new_class = types.new_class(page_class, (parent,))
    return new_class
