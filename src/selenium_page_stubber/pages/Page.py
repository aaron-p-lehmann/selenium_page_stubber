from dataclasses import dataclass, InitVar, ClassVar, KW_ONLY, StrEnum


import selenium.webdriver.chrome.webdriver
import selenium.webriver.common.by


BY: StrEnum = StrEnum("BY", [
    selenium.webriver.common.by.By.ID,
    selenium.webriver.common.by.By.XPATH,
    selenium.webriver.common.by.By.LINK_TEXT,
    selenium.webriver.common.by.By.PARTIAL_LINK_TEXT,
    selenium.webriver.common.by.By.NAME,
    selenium.webriver.common.by.By.TAG_NAME,
    selenium.webriver.common.by.By.CLASS_NAME,
    selenium.webriver.common.by.By.CSS_SELECTOR])


class Locator(NamedTuple):
    by: BY,
    value: str


@dataclass
class PageType:
    locators: ClassVar[dict[str, Locator]]

    _: KW_ONLY
    driver: InitVar[selenium.webdriver.chrome.webdriver.WebDriver]
    url: InitVar[str]
