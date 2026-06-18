import pytest
from pages.dashboard_page import DashboardPage
from pages.expense_form_page import ExpenseFormPage


@pytest.fixture
def seeded_page(page):
    """Seed 10+ diverse expenses so charts and insights have data."""
    entries = [
        ("12.50", "Supermarché", "Food"),
        ("45.00", "Restaurant", "Food"),
        ("28.00", "Essence", "Transport"),
        ("9.99", "Netflix", "Entertainment"),
        ("65.00", "Médecin", "Health"),
        ("120.00", "Vêtements", "Shopping"),
        ("18.00", "Café", "Food"),
        ("7.50", "Bus ticket", "Transport"),
        ("200.00", "Loyer part", "Housing"),
        ("35.00", "Sport", "Health"),
    ]
    page.goto("/")
    page.wait_for_load_state("networkidle")
    for amount, desc, cat in entries:
        DashboardPage(page).open_add_expense_form()
        ExpenseFormPage(page).add_expense(amount=amount, description=desc, category=cat)

    return page


# 15. Monthly spending chart renders with correct data
def test_spending_chart_renders(seeded_page):
    page = seeded_page
    page.goto("/")
    page.wait_for_load_state("networkidle")

    dashboard = DashboardPage(page)
    assert dashboard.is_chart_rendered(), "Recharts spending chart should be rendered on dashboard"

    # Chart should show EUR values — look for currency indicator
    assert (
        page.get_by_text("€").first.is_visible()
        or page.get_by_text("EUR").first.is_visible()
    ), "Chart should display EUR amounts"


# 16. AI spending insight returns a meaningful summary
@pytest.mark.integration
def test_ai_insight_generated(seeded_page):
    page = seeded_page
    page.goto("/")
    page.wait_for_load_state("networkidle")

    dashboard = DashboardPage(page)
    assert DashboardPage(seeded_page).is_chart_rendered(), \
        "Dashboard needs data before triggering insight"

    dashboard.trigger_ai_insight()
    page.wait_for_timeout(8000)  # Claude API may take a few seconds

    insight_text = page.locator("[data-testid='ai-insight'], .ai-insight, [aria-label*='insight']")
    assert insight_text.is_visible(), "AI insight container should appear after trigger"
    content = insight_text.inner_text()
    assert len(content) > 20, f"AI insight too short or empty: '{content}'"
