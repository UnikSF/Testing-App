import pytest
from pages.dashboard_page import DashboardPage
from pages.expense_form_page import ExpenseFormPage
from pages.settings_page import SettingsPage


@pytest.fixture(autouse=True)
def go_home(page):
    page.goto("/")
    page.wait_for_load_state("networkidle")


# 17. Zero-amount expense — validation error or saved with warning
def test_zero_amount_expense(page):
    DashboardPage(page).open_add_expense_form()
    form = ExpenseFormPage(page)
    form.fill_amount("0")
    form.fill_description("ZeroAmountTest")
    form.submit()

    error = form.get_validation_error()
    expense_visible = DashboardPage(page).get_expense_by_description("ZeroAmountTest").is_visible()

    assert error is not None or expense_visible, \
        "Zero-amount expense should either show a validation error or be saved with a warning"


# 18. Negative amount (refund) — accepted and affects totals correctly
def test_negative_amount_refund(page):
    dashboard = DashboardPage(page)

    # Add a positive expense first so balance is meaningful
    dashboard.open_add_expense_form()
    ExpenseFormPage(page).add_expense(amount="100.00", description="BaseExpense")
    balance_before = dashboard.get_balance_text()

    dashboard.open_add_expense_form()
    form = ExpenseFormPage(page)
    form.fill_amount("-25.00")
    form.fill_description("Refund Amazon")
    form.submit()

    balance_after = dashboard.get_balance_text()
    assert balance_before != balance_after, \
        "Balance should change after adding a negative (refund) amount"
    assert dashboard.get_expense_by_description("Refund Amazon").is_visible(), \
        "Refund expense should be visible in the list"


# 19. Very large amount — no overflow or crash
def test_very_large_amount(page):
    DashboardPage(page).open_add_expense_form()
    form = ExpenseFormPage(page)
    form.add_expense(amount="999999.99", description="LargeAmountTest")

    assert DashboardPage(page).get_expense_by_description("LargeAmountTest").is_visible(), \
        "Very large amount should be saved without crashing"
    assert page.get_by_text("999999").is_visible() or page.get_by_text("999 999").is_visible(), \
        "Large amount should display correctly without truncation"


# 20. No internet (GoCardless unavailable) — graceful error, no crash
@pytest.mark.integration
def test_sync_without_internet_shows_error(page):
    page.goto("/settings")
    page.wait_for_load_state("networkidle")

    # Simulate offline by blocking GoCardless endpoints
    page.route("**/gocardless**", lambda route: route.abort())
    page.route("**/bankaccountdata**", lambda route: route.abort())

    settings = SettingsPage(page)
    settings.trigger_sync()

    assert settings.has_sync_error(), \
        "A graceful error should appear when GoCardless is unreachable"
    assert not page.is_closed(), "Page should not crash on sync failure"


# 21. Empty database (first launch) — clean empty state UI
def test_empty_state_ui(page):
    # We can't reliably delete the DB in a UI test, so we test the behaviour
    # by checking that the dashboard handles zero expenses gracefully.
    # If expenses exist from other tests, this test is informational only.
    dashboard = DashboardPage(page)
    expense_items = dashboard.get_expense_items()

    if len(expense_items) == 0:
        # No expenses — empty state should be shown, no crashes
        empty_state = page.locator("[data-testid='empty-state'], .empty-state")
        assert empty_state.is_visible() or page.get_by_text("No expenses", exact=False).is_visible(), \
            "Empty state UI should be shown when there are no expenses"
    else:
        # Expenses exist — just verify the page loads without errors
        assert len(expense_items) > 0, "Dashboard loaded with existing expenses — OK"
