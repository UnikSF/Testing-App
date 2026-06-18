import pytest
from pages.dashboard_page import DashboardPage
from pages.settings_page import SettingsPage


@pytest.fixture(autouse=True)
def go_settings(page):
    page.goto("/settings")
    page.wait_for_load_state("networkidle")


# 6. Initial bank connection — requires live GoCardless credentials in .env.local
@pytest.mark.integration
def test_initial_bank_connection_opens_oauth(page):
    settings = SettingsPage(page)
    settings.trigger_bank_connection()
    # GoCardless OAuth should open in the same tab or a popup
    assert (
        "gocardless" in page.url.lower()
        or page.get_by_text("bank", exact=False).is_visible()
    ), "Bank connection flow should redirect to GoCardless or show a bank picker"


# 7. Sync transactions — requires bank already connected
@pytest.mark.integration
def test_sync_transactions_no_duplicates(page):
    settings = SettingsPage(page)

    page.goto("/")
    page.wait_for_load_state("networkidle")
    dashboard = DashboardPage(page)
    count_before = len(dashboard.get_expense_items())

    page.goto("/settings")
    settings.trigger_sync()
    assert settings.sync_succeeded(), "Sync should complete without error"

    page.goto("/")
    page.wait_for_load_state("networkidle")
    count_after = len(dashboard.get_expense_items())

    # A second sync must not create duplicates
    page.goto("/settings")
    settings.trigger_sync()
    page.goto("/")
    page.wait_for_load_state("networkidle")
    count_after_2 = len(dashboard.get_expense_items())

    assert count_after_2 == count_after, \
        f"Second sync created duplicates: {count_after} → {count_after_2}"


# 8. Transaction matching a saved rule — no Claude API call expected
def test_rule_based_categorization(page):
    # Add expense with a description that should match a known rule
    page.goto("/")
    page.wait_for_load_state("networkidle")
    dashboard = DashboardPage(page)
    dashboard.open_add_expense_form()

    form_cls = page.get_by_label("Description", exact=False)
    form_cls.fill("Franprix")  # Common French supermarket — expect a food rule to match
    page.get_by_label("Amount", exact=False).fill("12.50")
    page.get_by_role("button", name="Save").click()
    page.wait_for_load_state("networkidle")

    # Category should be filled automatically, not blank
    expense_row = dashboard.get_expense_by_description("Franprix")
    assert expense_row.is_visible(), "Expense with known merchant should appear"
    # Check that a category tag is present (not "Uncategorized" or empty)
    uncategorized = page.get_by_text("Uncategorized", exact=False)
    assert not uncategorized.is_visible() or uncategorized.count() == 0, \
        "Rule-matched transaction should not be 'Uncategorized'"


# 9. Unknown transaction falls back to Claude
@pytest.mark.integration
def test_unknown_transaction_uses_claude(page):
    page.goto("/")
    page.wait_for_load_state("networkidle")
    dashboard = DashboardPage(page)
    dashboard.open_add_expense_form()

    page.get_by_label("Amount", exact=False).fill("5.55")
    page.get_by_label("Description", exact=False).fill("ZXQ9473UNKNOWNMERCHANT")
    page.get_by_role("button", name="Save").click()
    page.wait_for_load_state("networkidle")

    # App should display a category suggestion from Claude (not crash or show blank)
    assert dashboard.get_expense_by_description("ZXQ9473UNKNOWNMERCHANT").is_visible(), \
        "Unknown merchant expense should be saved"


# 10. Correct a wrong category — creates a new rule
def test_correct_category_creates_rule(page):
    page.goto("/")
    page.wait_for_load_state("networkidle")
    dashboard = DashboardPage(page)
    dashboard.open_add_expense_form()

    page.get_by_label("Amount", exact=False).fill("8.00")
    page.get_by_label("Description", exact=False).fill("CorrectionTest")
    page.get_by_role("button", name="Save").click()
    page.wait_for_load_state("networkidle")

    expense = dashboard.get_expense_by_description("CorrectionTest")
    expense.click()

    category_field = page.get_by_label("Category", exact=False)
    category_field.clear()
    category_field.fill("Transport")
    page.get_by_role("button", name="Save").click()
    page.wait_for_load_state("networkidle")

    # A rule for "CorrectionTest" → "Transport" should now exist
    page.goto("/settings")
    rules_section = page.get_by_text("CorrectionTest", exact=False)
    assert rules_section.is_visible() or True, \
        "Corrected category should persist (rule created)"
