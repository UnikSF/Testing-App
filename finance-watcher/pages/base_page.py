from playwright.sync_api import Page, expect, Locator


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate(self, path: str = "/"):
        self.page.goto(path)
        self.page.wait_for_load_state("networkidle")

    def click(self, locator: Locator):
        locator.click()

    def fill(self, locator: Locator, value: str):
        locator.clear()
        locator.fill(value)

    def is_visible(self, locator: Locator, timeout: int = 5000) -> bool:
        try:
            locator.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def get_text(self, locator: Locator) -> str:
        return locator.inner_text()
