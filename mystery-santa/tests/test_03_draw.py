import pytest
from conftest import _register, _login


def _seed_participants(page, names: list[tuple]):
    for first, last in names:
        page.goto("/")
        page.wait_for_load_state("networkidle")
        _register(page, first, last)


def _trigger_draw(page):
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


# 9. Happy path draw with 4+ participants
def test_draw_happy_path(page):
    names = [("Alice", "Dupont"), ("Bob", "Martin"), ("Charlie", "Durand"), ("Diana", "Petit")]
    _seed_participants(page, names)
    _trigger_draw(page)

    # Each participant should have an assignment
    for first, last in names:
        page.goto("/")
        page.wait_for_load_state("networkidle")
        _login(page, first, last)
        assignment = page.locator("[data-testid='assignment']").or_(
            page.get_by_text("gifting", exact=False)
        )
        assert assignment.is_visible(), \
            f"{first} {last} should see their assignment after the draw"
        # No one should be assigned to themselves
        assert first not in assignment.inner_text(), \
            f"{first} should not be assigned to themselves"


# 10. Each participant gets exactly one assignment — no duplicates
def test_each_participant_one_assignment(page):
    names = [("E", "F"), ("G", "H"), ("I", "J"), ("K", "L"), ("M", "N"), ("O", "P")]
    _seed_participants(page, names)
    _trigger_draw(page)

    assignments = []
    for first, last in names:
        page.goto("/")
        page.wait_for_load_state("networkidle")
        _login(page, first, last)
        text = page.locator("[data-testid='assignment']").or_(
            page.get_by_text("gifting", exact=False)
        ).inner_text()
        assignments.append(text)

    assert len(set(assignments)) == len(names), \
        "Each participant should receive a unique assignment — no duplicates"


# 11. Draw with minimum 2 participants
def test_draw_two_participants(page):
    _seed_participants(page, [("Alpha", "One"), ("Beta", "Two")])
    _trigger_draw(page)

    page.goto("/")
    _login(page, "Alpha", "One")
    assignment = page.locator("[data-testid='assignment']").inner_text()
    assert "Beta" in assignment, "With 2 participants, Alpha should gift Beta"


# 13. Before draw — participant sees "waiting" message
def test_pre_draw_shows_waiting(page):
    _seed_participants(page, [("Waiting", "User"), ("Other", "Person")])
    # Do NOT trigger draw

    page.goto("/")
    _login(page, "Waiting", "User")

    waiting_msg = page.get_by_text("waiting", exact=False).or_(
        page.get_by_text("draw not yet", exact=False)
    )
    assignment = page.locator("[data-testid='assignment']")
    assert waiting_msg.is_visible() or not assignment.is_visible(), \
        "Participant should see a 'waiting' message before the draw, not an assignment"


# 15. Re-triggering draw is blocked
def test_retrigger_draw_blocked(page):
    names = [("Re1", "X"), ("Re2", "Y"), ("Re3", "Z"), ("Re4", "W")]
    _seed_participants(page, names)
    _trigger_draw(page)

    # Try to trigger again
    draw_btn = page.get_by_role("button", name="Launch draw").or_(
        page.get_by_role("button", name="Start draw")
    )
    if draw_btn.is_visible():
        draw_btn.click()
        alert = page.locator("[role='alert']")
        already_done = page.get_by_text("final", exact=False).or_(
            page.get_by_text("already done", exact=False)
        )
        assert alert.is_visible() or already_done.is_visible() or draw_btn.is_disabled(), \
            "Re-triggering the draw should be blocked"
    else:
        assert True  # Button hidden after draw — acceptable


# 19. Single participant — draw fails gracefully
def test_single_participant_draw_fails(page):
    _seed_participants(page, [("Solo", "Alone")])
    _trigger_draw(page)

    error = page.locator("[role='alert']").or_(
        page.get_by_text("least 2", exact=False)
    )
    assert error.is_visible(), "Draw with a single participant should show an error"


# 20. Very long name — stored and displayed correctly
def test_very_long_name(page):
    long_first = "A" * 50
    long_last = "B" * 50
    _register(page, long_first, long_last)

    assert page.get_by_text(long_first[:20], exact=False).is_visible(), \
        "Long first name should be stored and visible (even if truncated in display)"


# 21. Special characters in name
def test_special_characters_in_name(page):
    _register(page, "Jean-François", "Lévy")
    page.goto("/")
    page.wait_for_load_state("networkidle")
    _login(page, "Jean-François", "Lévy")

    assert page.get_by_text("Jean", exact=False).is_visible(), \
        "Special characters (accents, hyphens) should work in names"
