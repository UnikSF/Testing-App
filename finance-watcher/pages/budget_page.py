from playwright.sync_api import Page
from .base_page import BasePage


class BudgetPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.create_budget_btn = page.get_by_role("button", name="Create Budget")
        self.budget_name_input = page.get_by_label("Name", exact=False)
        self.budget_limit_input = page.get_by_label("Limit", exact=False)
        self.budget_period_select = page.get_by_label("Period", exact=False)
        self.save_btn = page.get_by_role("button", name="Save")
        self.budget_cards = page.locator("[data-testid='budget-card'], .budget-card")
        self.progress_bars = page.locator("[role='progressbar']")
        self.over_budget_indicator = page.locator("[data-testid='over-budget'], .text-red, [class*='red']")
        self.savings_goal_btn = page.get_by_role("button", name="Create Goal")
        self.goal_name_input = page.get_by_label("Goal name", exact=False)
        self.goal_target_input = page.get_by_label("Target amount", exact=False)
        self.goal_date_input = page.get_by_label("Target date", exact=False)

    def open_create_budget(self):
        self.create_budget_btn.click()

    def create_budget(self, name: str, limit: str, period: str = "monthly"):
        self.open_create_budget()
        self.fill(self.budget_name_input, name)
        self.fill(self.budget_limit_input, limit)
        if period:
            self.budget_period_select.select_option(label=period)
        self.save_btn.click()
        self.page.wait_for_load_state("networkidle")

    def get_budget_count(self) -> int:
        return self.budget_cards.count()

    def is_over_budget(self) -> bool:
        return self.is_visible(self.over_budget_indicator)

    def get_progress_values(self) -> list[str]:
        bars = self.progress_bars.all()
        return [b.get_attribute("aria-valuenow") or b.get_attribute("value") or "" for b in bars]

    def create_savings_goal(self, name: str, target: str, date: str):
        self.savings_goal_btn.click()
        self.fill(self.goal_name_input, name)
        self.fill(self.goal_target_input, target)
        self.fill(self.goal_date_input, date)
        self.save_btn.click()
        self.page.wait_for_load_state("networkidle")
