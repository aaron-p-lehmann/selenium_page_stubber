from dataclasses import dataclass, InitVar, KW_ONLY
from enum import StrEnum
from typing import ClassVar, NamedTuple


import selenium.webdriver.chrome.webdriver
import selenium.webdriver.common.by


class BY(StrEnum):
    ID = selenium.webdriver.common.by.By.ID
    XPATH = selenium.webdriver.common.by.By.XPATH
    LINK_TEXT = selenium.webdriver.common.by.By.LINK_TEXT
    PARTIAL_LINK_TEXT = selenium.webdriver.common.by.By.PARTIAL_LINK_TEXT
    NAME = selenium.webdriver.common.by.By.NAME
    TAG_NAME = selenium.webdriver.common.by.By.TAG_NAME
    CLASS_NAME = selenium.webdriver.common.by.By.CLASS_NAME
    CSS_SELECTOR = selenium.webdriver.common.by.By.CSS_SELECTOR


class Locator(NamedTuple):
    by: BY
    value: str


@dataclass
class Page:
    locators: ClassVar[dict[str, Locator]]

    _: KW_ONLY
    driver: InitVar[selenium.webdriver.chrome.webdriver.WebDriver]
    url: InitVar[str]

    def __init__(self, *, driver, url):
        self.driver = driver
        self.url = url
