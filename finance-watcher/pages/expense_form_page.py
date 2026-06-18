# Selectors are based on expected Next.js form conventions (label → input association).
# Verify with browser DevTools and adjust label text to match the actual UI language.
from playwright.sync_api import Page
from .base_page import BasePage


class ExpenseFormPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.amount_input = page.get_by_label("Amount", exact=False)
        self.description_input = page.get_by_label("Description", exact=False)
        self.category_input = page.get_by_label("Category", exact=False)
        self.date_input = page.get_by_label("Date", exact=False)
        self.save_btn = page.get_by_role("button", name="Save")
        self.cancel_btn = page.get_by_role("button", name="Cancel")
        self.form = page.locator("form, dialog, [role='dialog']")
        self.validation_error = page.locator("[data-testid='error'], .error-message, [role='alert']")

    def is_open(self) -> bool:
        return self.is_visible(self.form)

    def fill_amount(self, amount: str):
        self.fill(self.amount_input, amount)

    def fill_description(self, description: str):
        self.fill(self.description_input, description)

    def select_category(self, category: str):
        # Handles both <select> and combobox patterns
        if self.category_input.get_attribute("role") == "combobox":
            self.category_input.click()
            self.page.get_by_role("option", name=category).click()
        else:
            self.category_input.select_option(label=category)

    def fill_date(self, date_str: str):
        # date_str in "YYYY-MM-DD" format
        self.fill(self.date_input, date_str)

    def submit(self):
        self.save_btn.click()
        self.page.wait_for_load_state("networkidle")

    def cancel(self):
        self.cancel_btn.click()

    def get_validation_error(self) -> str | None:
        if self.is_visible(self.validation_error, timeout=2000):
            return self.get_text(self.validation_error)
        return None

    def add_expense(self, amount: str, description: str, category: str = "", date: str = ""):
        self.fill_amount(amount)
        self.fill_description(description)
        if category:
            self.select_category(category)
        if date:
            self.fill_date(date)
        self.submit()
