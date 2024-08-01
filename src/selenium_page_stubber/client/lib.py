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
import selenium_page_stubber.user.pages.Page


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
        template_name: str,
        parent: type = selenium_page_stubber.user.pages.Page.Page) -> type:
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


def copy_with_possible_suffix(
        data: str, target: pathlib.Path, suffix: str = ".new") -> None:
    """Copy src to target, or to <targetname>.new, if target already exists.
    Don't copy anything if the file already exists and has the same data."""
    suffix = f".{suffix.lstrip('.')}"
    if target.suffix == suffix:
        raise ValueError(
            f"'{target}' has the same suffix as the one provided: '{suffix}'")
    try:
        existing_data = target.read_text()
        if existing_data != data:
            target = target.with_suffix(suffix)
            target.write_text(data)
    except FileNotFoundError:
        target.write_text(data)


def initialize(
        pages_src: pathlib.Path,
        pages_target: pathlib.Path,
        templates_src: pathlib.Path,
        templates_target: pathlib.Path) -> None:
    """Create page_directory and template_directory, if necessary, then copy
    everything over from the "user" directories."""
    pages_target.mkdir(exist_ok=True)
    templates_target.mkdir(exist_ok=True)

    for f in pages_src.iterdir():
        if f.is_file():
            copy_with_possible_suffix(f.read_text(), pages_target / f.name)
    for f in templates_src.iterdir():
        if f.is_file():
            copy_with_possible_suffix(f.read_text(), templates_target / f.name)
