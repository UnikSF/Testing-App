from playwright.sync_api import Page
from .base_page import BasePage


class SettingsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.connect_bank_btn = page.get_by_role("button", name="Connect bank")
        self.sync_btn = page.get_by_role("button", name="Sync")
        self.bank_status = page.locator("[data-testid='bank-status']")
        self.sync_success_msg = page.get_by_text("Sync complete", exact=False)
        self.sync_error_msg = page.locator("[data-testid='sync-error'], [role='alert']")
        self.no_internet_msg = page.get_by_text("connexion", exact=False)
        self.recurring_section = page.locator("[data-testid='recurring-transactions']")

    def trigger_bank_connection(self):
        self.connect_bank_btn.click()

    def trigger_sync(self):
        self.sync_btn.click()
        self.page.wait_for_load_state("networkidle")

    def is_bank_connected(self) -> bool:
        return self.is_visible(self.bank_status) and "connected" in self.get_text(self.bank_status).lower()

    def sync_succeeded(self) -> bool:
        return self.is_visible(self.sync_success_msg, timeout=10000)

    def has_sync_error(self) -> bool:
        return self.is_visible(self.sync_error_msg, timeout=5000)

    def is_no_internet_error_shown(self) -> bool:
        return self.has_sync_error()
