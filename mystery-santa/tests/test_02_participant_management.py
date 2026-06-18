import pytest
from conftest import _register


@pytest.fixture
def four_participants(page):
    names = [("Alice", "Dupont"), ("Bob", "Martin"), ("Charlie", "Durand"), ("Diana", "Petit")]
    for first, last in names:
        page.goto("/")
        page.wait_for_load_state("networkidle")
        _register(page, first, last)
    return names


# 6. Organizer can view all participants
def test_organizer_sees_all_participants(page, four_participants):
    page.goto("/admin")
    page.wait_for_load_state("networkidle")

    for first, _ in four_participants:
        assert page.get_by_text(first, exact=False).is_visible(), \
            f"Organizer should see '{first}' in the participant list"


# 7. Remove a participant before the draw
def test_remove_participant_before_draw(page, four_participants):
    page.goto("/admin")
    page.wait_for_load_state("networkidle")

    remove_btn = page.get_by_role("button", name="Remove").first
    remove_btn.click()
    confirm = page.get_by_role("button", name="Confirm")
    if confirm.is_visible():
        confirm.click()
    page.wait_for_load_state("networkidle")

    participants = page.locator("[data-testid='participant-item'], .participant").all()
    assert len(participants) == len(four_participants) - 1, \
        "Participant list should shrink by 1 after removal"


# 8. Cannot remove participant after draw
def test_cannot_remove_after_draw(page, four_participants):
    page.goto("/admin")
    page.wait_for_load_state("networkidle")

    draw_btn = page.get_by_role("button", name="Launch draw").or_(
        page.get_by_role("button", name="Start draw")
    )
    draw_btn.click()
    confirm = page.get_by_role("button", name="Confirm")
    if confirm.is_visible():
        confirm.click()
    page.wait_for_load_state("networkidle")

    remove_btn = page.get_by_role("button", name="Remove").first
    is_disabled = remove_btn.is_disabled()
    if not is_disabled:
        remove_btn.click()
        alert = page.locator("[role='alert']")
        assert alert.is_visible(), "Removing after draw should be blocked with a warning"
    else:
        assert is_disabled, "Remove buttons should be disabled after the draw is triggered"
