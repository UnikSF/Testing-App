# Selectors are based on expected Next.js/React UI conventions.
# Verify with browser DevTools against the running app and adjust as needed.
from playwright.sync_api import Page
from .base_page import BasePage


class DashboardPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.add_expense_btn = page.get_by_role("button", name="Add Expense")
        self.expense_list = page.locator("[data-testid='expense-list'], ul[aria-label*='expense'], table")
        self.balance_display = page.locator("[data-testid='balance'], [data-testid='total']")
        self.chart_container = page.locator("[data-testid='spending-chart'], .recharts-wrapper")
        self.ai_insight_btn = page.get_by_role("button", name="AI Insight")

    def open_add_expense_form(self):
        self.add_expense_btn.click()

    def get_expense_items(self):
        return self.expense_list.locator("li, tr, [data-testid='expense-item']").all()

    def get_balance_text(self) -> str:
        return self.get_text(self.balance_display)

    def is_chart_rendered(self) -> bool:
        return self.is_visible(self.chart_container)

    def trigger_ai_insight(self):
        self.ai_insight_btn.click()

    def get_expense_by_description(self, description: str):
        return self.page.get_by_text(description, exact=False)

    def navigate_to_budgets(self):
        self.page.get_by_role("link", name="Budget").click()
        self.page.wait_for_load_state("networkidle")

    def navigate_to_settings(self):
        self.page.get_by_role("link", name="Settings").click()
        self.page.wait_for_load_state("networkidle")
