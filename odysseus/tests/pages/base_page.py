from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def is_visible(self, locator, timeout: int = 5000) -> bool:
        try:
            locator.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def get_text(self, locator) -> str:
        return locator.inner_text()
