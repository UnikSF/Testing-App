import pytest
from datetime import date, timedelta
from pages.dashboard_page import DashboardPage
from pages.expense_form_page import ExpenseFormPage


@pytest.fixture(autouse=True)
def go_home(page):
    page.goto("/")
    page.wait_for_load_state("networkidle")


# 1. Add a basic expense
def test_add_basic_expense(page):
    dashboard = DashboardPage(page)
    initial_count = len(dashboard.get_expense_items())

    dashboard.open_add_expense_form()

    form = ExpenseFormPage(page)
    assert form.is_open(), "Expense form did not open"
    form.add_expense(amount="15.50", description="Lunch", category="Food")

    assert len(dashboard.get_expense_items()) == initial_count + 1, \
        "Expense count did not increase after adding"
    assert dashboard.get_expense_by_description("Lunch").is_visible(), \
        "Newly added expense 'Lunch' not visible in list"


# 2. Add expense with no category — auto-categorization should trigger
def test_add_expense_without_category(page):
    dashboard = DashboardPage(page)
    dashboard.open_add_expense_form()

    form = ExpenseFormPage(page)
    form.fill_amount("22.00")
    form.fill_description("Unknown shop 42")
    form.submit()

    # App should save and assign a category (via rules or Claude API fallback)
    assert dashboard.get_expense_by_description("Unknown shop 42").is_visible(), \
        "Uncategorized expense should be saved and appear in list"


# 3. Edit an existing expense
def test_edit_existing_expense(page):
    dashboard = DashboardPage(page)
    dashboard.open_add_expense_form()
    form = ExpenseFormPage(page)
    form.add_expense(amount="15.00", description="EditTest")

    expense = dashboard.get_expense_by_description("EditTest")
    expense.click()

    form2 = ExpenseFormPage(page)
    form2.fill_amount("20.00")
    form2.submit()

    assert dashboard.get_expense_by_description("EditTest").is_visible(), \
        "Edited expense should still appear"
    assert page.get_by_text("20.00").is_visible() or page.get_by_text("20,00").is_visible(), \
        "Updated amount should be visible"


# 4. Delete an expense
def test_delete_expense(page):
    dashboard = DashboardPage(page)
    dashboard.open_add_expense_form()
    form = ExpenseFormPage(page)
    form.add_expense(amount="9.99", description="DeleteMe")

    initial_count = len(dashboard.get_expense_items())

    delete_btn = page.get_by_role("button", name="Delete").first
    delete_btn.click()
    # Confirm if a confirmation dialog appears
    confirm = page.get_by_role("button", name="Confirm")
    if confirm.is_visible():
        confirm.click()
    page.wait_for_load_state("networkidle")

    assert len(dashboard.get_expense_items()) < initial_count, \
        "Expense count should decrease after deletion"


# 5. Add a future-dated expense
def test_add_future_dated_expense(page):
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    dashboard = DashboardPage(page)
    dashboard.open_add_expense_form()

    form = ExpenseFormPage(page)
    form.add_expense(amount="30.00", description="FutureExpense", date=tomorrow)

    assert dashboard.get_expense_by_description("FutureExpense").is_visible(), \
        "Future-dated expense should be saved and appear in the list"
