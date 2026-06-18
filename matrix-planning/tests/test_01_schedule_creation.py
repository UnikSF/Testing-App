# Tests for Matrix Planning — schedule creation scenarios.
# App not yet built: these tests define the expected behaviour and will fail until implemented.
import pytest


@pytest.fixture
def slot_form(page):
    page.get_by_role("button", name="Add slot").or_(
        page.get_by_role("button", name="Add class")
    ).click()
    page.wait_for_load_state("networkidle")
    return page


def _add_slot(page, subject: str, teacher: str, room: str, day: str, start: str, end: str):
    page.get_by_label("Subject", exact=False).fill(subject)
    page.get_by_label("Teacher", exact=False).fill(teacher)
    page.get_by_label("Room", exact=False).fill(room)
    page.get_by_label("Day", exact=False).select_option(label=day)
    page.get_by_label("Start time", exact=False).fill(start)
    page.get_by_label("End time", exact=False).fill(end)
    page.get_by_role("button", name="Save").click()
    page.wait_for_load_state("networkidle")


# 1. Add a class slot
def test_add_class_slot(page, slot_form):
    _add_slot(page, "Maths", "Prof. Martin", "A101", "Monday", "08:00", "10:00")

    grid_slot = page.get_by_text("Maths", exact=False)
    assert grid_slot.is_visible(), "Added class slot should appear in the weekly grid"


# 2. Add multiple slots for the same subject on different days
def test_add_multiple_slots_same_subject(page, slot_form):
    _add_slot(page, "English", "Prof. Smith", "B202", "Monday", "10:00", "12:00")

    page.get_by_role("button", name="Add slot").or_(
        page.get_by_role("button", name="Add class")
    ).click()
    _add_slot(page, "English", "Prof. Smith", "B202", "Wednesday", "14:00", "16:00")

    slots = page.get_by_text("English", exact=False).all()
    assert len(slots) >= 2, "Both English slots (Mon + Wed) should appear in the grid"


# 3. Fill a full week — no overlap in rendered grid
def test_full_week_schedule_renders(page):
    subjects = [
        ("Physics", "Prof. Curie", "C301", "Monday", "08:00", "10:00"),
        ("Chemistry", "Prof. Bohr", "C302", "Tuesday", "08:00", "10:00"),
        ("History", "Prof. Hugo", "A101", "Wednesday", "08:00", "10:00"),
        ("Geography", "Prof. Verne", "A102", "Thursday", "08:00", "10:00"),
        ("Biology", "Prof. Darwin", "B201", "Friday", "08:00", "10:00"),
    ]
    for s in subjects:
        page.get_by_role("button", name="Add slot").or_(
            page.get_by_role("button", name="Add class")
        ).click()
        _add_slot(page, *s)

    conflict_icons = page.locator("[data-testid='conflict'], .conflict-indicator")
    assert conflict_icons.count() == 0, "No conflicts expected for non-overlapping full week"
