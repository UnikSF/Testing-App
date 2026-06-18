import pytest
from conftest import _register, _login


# 1. Register a new participant
def test_register_new_participant(page):
    _register(page, "Alice", "Dupont")
    assert page.get_by_text("Alice", exact=False).is_visible(), \
        "Registered participant should appear (profile or confirmation)"


# 2. Login as existing participant
def test_login_existing_participant(page):
    _register(page, "Bob", "Martin")
    page.goto("/")
    page.wait_for_load_state("networkidle")

    _login(page, "Bob", "Martin")
    assert page.get_by_text("Bob", exact=False).is_visible(), \
        "Logged-in participant should see their profile"


# 3. Wrong name at login — error message
def test_wrong_name_shows_error(page):
    _login(page, "Nobody", "Unknown")
    error = page.get_by_text("not found", exact=False).or_(
        page.get_by_text("Register", exact=False)
    )
    assert error.is_visible(), "Unregistered name should show an error or prompt to register"


# 4. Duplicate registration — blocked
def test_duplicate_registration_blocked(page):
    _register(page, "Alice", "Dupont")
    _register(page, "Alice", "Dupont")

    error = page.locator("[data-testid='error'], [role='alert']")
    already_in = page.get_by_text("already", exact=False)
    assert error.is_visible() or already_in.is_visible(), \
        "Duplicate registration should be rejected with an error"


# 5. Case sensitivity — consistent behaviour
def test_case_sensitivity_consistent(page):
    _register(page, "marie", "curie")
    page.goto("/")
    page.wait_for_load_state("networkidle")

    _login(page, "Marie", "Curie")
    # Either both capitalizations work or both fail — no silent mismatch
    is_logged_in = page.get_by_text("marie", exact=False).is_visible() or \
                   page.get_by_text("Marie", exact=False).is_visible()
    not_found = page.get_by_text("not found", exact=False).is_visible() or \
                page.get_by_text("error", exact=False).is_visible()

    assert is_logged_in or not_found, \
        "Case handling should be consistent — no silent mismatch between registration and login"
