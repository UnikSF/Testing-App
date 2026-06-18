import pytest
from pages.dashboard_page import DashboardPage
from pages.expense_form_page import ExpenseFormPage
from pages.budget_page import BudgetPage


@pytest.fixture(autouse=True)
def go_budgets(page):
    page.goto("/budgets")
    page.wait_for_load_state("networkidle")


# 11. Create a budget
def test_create_budget(page):
    budget = BudgetPage(page)
    initial_count = budget.get_budget_count()

    budget.create_budget(name="Groceries", limit="200", period="monthly")

    assert budget.get_budget_count() == initial_count + 1, \
        "Budget count should increase after creation"
    assert page.get_by_text("Groceries").is_visible(), "Created budget should appear in list"
    assert page.get_by_text("200").is_visible() or page.get_by_text("200,00").is_visible(), \
        "Budget limit (200 EUR) should be displayed"


# 12. Budget exceeded — progress bar / indicator turns red
def test_budget_exceeded_shows_warning(page):
    budget = BudgetPage(page)
    budget.create_budget(name="OverBudgetTest", limit="5", period="monthly")

    # Add expenses that exceed the 5 EUR budget
    page.goto("/")
    page.wait_for_load_state("networkidle")
    dashboard = DashboardPage(page)
    dashboard.open_add_expense_form()
    form = ExpenseFormPage(page)
    form.add_expense(amount="10.00", description="Over limit spend", category="OverBudgetTest")

    page.goto("/budgets")
    page.wait_for_load_state("networkidle")

    assert BudgetPage(page).is_over_budget(), \
        "Over-budget indicator should be visible when spending exceeds limit"


# 13. Create a savings goal
def test_create_savings_goal(page):
    budget = BudgetPage(page)
    budget.create_savings_goal(name="Vacation", target="1000", date="2026-12-31")

    assert page.get_by_text("Vacation").is_visible(), "Savings goal should appear"
    assert page.get_by_text("1000").is_visible() or page.get_by_text("1 000").is_visible(), \
        "Goal target amount should be displayed"
    # Monthly amount needed should be shown
    monthly_label = page.get_by_text("per month", exact=False)
    assert monthly_label.is_visible(), "Monthly savings needed should be displayed"


# 14. Recurring transaction detected after 3 identical imports
@pytest.mark.integration
def test_recurring_transaction_detected(page):
    # Add the same merchant 3 times (simulating 3 months of bank sync)
    descriptions = ["Netflix Subscription"] * 3
    for desc in descriptions:
        page.goto("/")
        page.wait_for_load_state("networkidle")
        DashboardPage(page).open_add_expense_form()
        form = ExpenseFormPage(page)
        form.add_expense(amount="15.99", description=desc)

    page.goto("/budgets")
    page.wait_for_load_state("networkidle")

    recurring_section = page.get_by_text("Recurring", exact=False)
    assert recurring_section.is_visible(), "Recurring transactions section should appear"
    assert page.get_by_text("Netflix", exact=False).is_visible(), \
        "Netflix should be flagged as a recurring transaction"
