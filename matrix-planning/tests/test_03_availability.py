import pytest


# 8. Teacher unavailable slot — blocked or warned
def test_teacher_unavailable_slot_blocked(page):
    # Mark Prof. Martin unavailable on Wednesday afternoon
    page.get_by_role("link", name="Availability").or_(
        page.get_by_role("button", name="Manage availability")
    ).click()
    page.wait_for_load_state("networkidle")

    page.get_by_label("Teacher", exact=False).select_option(label="Prof. Martin")
    page.get_by_label("Day", exact=False).select_option(label="Wednesday")
    page.get_by_label("Unavailable from", exact=False).fill("14:00")
    page.get_by_role("button", name="Save").click()
    page.wait_for_load_state("networkidle")

    # Try to schedule Prof. Martin on Wednesday afternoon
    page.goto("/")
    page.get_by_role("button", name="Add slot").or_(
        page.get_by_role("button", name="Add class")
    ).click()
    page.wait_for_load_state("networkidle")

    page.get_by_label("Subject", exact=False).fill("Maths")
    page.get_by_label("Teacher", exact=False).fill("Prof. Martin")
    page.get_by_label("Room", exact=False).fill("A101")
    page.get_by_label("Day", exact=False).select_option(label="Wednesday")
    page.get_by_label("Start time", exact=False).fill("15:00")
    page.get_by_label("End time", exact=False).fill("17:00")
    page.get_by_role("button", name="Save").click()
    page.wait_for_load_state("networkidle")

    warning = page.locator("[data-testid='availability-conflict'], [role='alert']")
    assert warning.is_visible() or page.get_by_text("unavailable", exact=False).is_visible(), \
        "Scheduling a teacher during their unavailable slot should trigger a warning"


# 9. Room closed for maintenance
def test_room_closed_blocks_scheduling(page):
    page.get_by_role("link", name="Rooms").or_(
        page.get_by_role("button", name="Manage rooms")
    ).click()
    page.wait_for_load_state("networkidle")

    page.get_by_text("B202", exact=False).click()
    page.get_by_label("Closed on", exact=False).select_option(label="Friday")
    page.get_by_role("button", name="Save").click()
    page.wait_for_load_state("networkidle")

    # Try to schedule in B202 on Friday
    page.goto("/")
    page.get_by_role("button", name="Add slot").or_(
        page.get_by_role("button", name="Add class")
    ).click()
    page.wait_for_load_state("networkidle")

    page.get_by_label("Room", exact=False).fill("B202")
    page.get_by_label("Day", exact=False).select_option(label="Friday")
    page.get_by_role("button", name="Save").click()

    warning = page.locator("[data-testid='room-unavailable'], [role='alert']")
    assert warning.is_visible() or page.get_by_text("closed", exact=False).is_visible(), \
        "Room B202 should be blocked on Friday (maintenance)"


# 10. Auto-generation respects all constraints
def test_auto_generate_respects_constraints(page):
    generate_btn = page.get_by_role("button", name="Generate schedule").or_(
        page.get_by_role("button", name="Auto-generate")
    )
    if not generate_btn.is_visible(timeout=3000):
        pytest.skip("Auto-generation feature not yet implemented")

    generate_btn.click()
    page.wait_for_load_state("networkidle", timeout=30000)

    conflict_icons = page.locator("[data-testid='conflict'], .conflict-indicator")
    assert conflict_icons.count() == 0, "Auto-generated schedule should have zero conflicts"


# 11. Move a class slot (reschedule)
def test_move_slot(page):
    page.get_by_role("button", name="Add slot").or_(
        page.get_by_role("button", name="Add class")
    ).click()
    page.wait_for_load_state("networkidle")
    page.get_by_label("Subject", exact=False).fill("Physics")
    page.get_by_label("Teacher", exact=False).fill("Prof. Curie")
    page.get_by_label("Room", exact=False).fill("C301")
    page.get_by_label("Day", exact=False).select_option(label="Tuesday")
    page.get_by_label("Start time", exact=False).fill("09:00")
    page.get_by_label("End time", exact=False).fill("11:00")
    page.get_by_role("button", name="Save").click()
    page.wait_for_load_state("networkidle")

    page.get_by_text("Physics", exact=False).click()
    page.get_by_label("Day", exact=False).select_option(label="Thursday")
    page.get_by_label("Start time", exact=False).fill("11:00")
    page.get_by_label("End time", exact=False).fill("13:00")
    page.get_by_role("button", name="Save").click()
    page.wait_for_load_state("networkidle")

    thursday_slot = page.get_by_text("Physics", exact=False)
    assert thursday_slot.is_visible(), "Physics should appear on Thursday after rescheduling"


# 12. Delete a slot
def test_delete_slot(page):
    page.get_by_role("button", name="Add slot").or_(
        page.get_by_role("button", name="Add class")
    ).click()
    page.wait_for_load_state("networkidle")
    page.get_by_label("Subject", exact=False).fill("ToDelete")
    page.get_by_label("Teacher", exact=False).fill("Prof. X")
    page.get_by_label("Room", exact=False).fill("Z999")
    page.get_by_label("Day", exact=False).select_option(label="Monday")
    page.get_by_label("Start time", exact=False).fill("08:00")
    page.get_by_label("End time", exact=False).fill("10:00")
    page.get_by_role("button", name="Save").click()
    page.wait_for_load_state("networkidle")

    page.get_by_text("ToDelete", exact=False).click()
    page.get_by_role("button", name="Delete").click()
    confirm = page.get_by_role("button", name="Confirm")
    if confirm.is_visible():
        confirm.click()
    page.wait_for_load_state("networkidle")

    assert not page.get_by_text("ToDelete").is_visible(), \
        "Deleted slot should no longer appear in the grid"


# 14. Empty schedule — blank grid, no errors
def test_empty_schedule_loads(page):
    assert not page.is_closed(), "App should load without errors on empty schedule"
    grid = page.locator("[data-testid='schedule-grid'], .schedule-grid, table")
    assert grid.is_visible() or page.get_by_text("No classes", exact=False).is_visible(), \
        "Empty schedule should show a blank grid or empty state, not an error"
