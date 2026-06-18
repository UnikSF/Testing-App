import pytest
from conftest import _register, _login


# 16. PWA installable — manifest and service worker present
def test_pwa_manifest_present(page):
    manifest_link = page.locator("link[rel='manifest']")
    assert manifest_link.count() > 0, "Page should include a <link rel='manifest'> for PWA install"

    manifest_href = manifest_link.get_attribute("href")
    assert manifest_href, "Manifest link should have a valid href"

    resp = page.request.get(manifest_href)
    assert resp.ok, f"Manifest file should be accessible, got HTTP {resp.status}"

    manifest = resp.json()
    assert "name" in manifest or "short_name" in manifest, \
        "Manifest should include app name"
    assert "icons" in manifest, "Manifest should include icons for PWA install"


def test_service_worker_registered(page):
    is_sw_registered = page.evaluate("""async () => {
        if (!('serviceWorker' in navigator)) return false;
        const regs = await navigator.serviceWorker.getRegistrations();
        return regs.length > 0;
    }""")
    assert is_sw_registered, "A service worker should be registered for offline PWA support"


# 17. View assignment offline — cached after first load
def test_assignment_visible_offline(page):
    _register(page, "OfflineUser", "Test")

    # Seed a second participant and trigger draw via admin
    page.goto("/")
    page.wait_for_load_state("networkidle")
    _register(page, "OfflineUser2", "Test")
    page.goto("/admin")
    page.wait_for_load_state("networkidle")

    draw_btn = page.get_by_role("button", name="Launch draw").or_(
        page.get_by_role("button", name="Start draw")
    )
    if draw_btn.is_visible():
        draw_btn.click()
        confirm = page.get_by_role("button", name="Confirm")
        if confirm.is_visible():
            confirm.click()
        page.wait_for_load_state("networkidle")

    # Login to load assignment into cache
    page.goto("/")
    page.wait_for_load_state("networkidle")
    _login(page, "OfflineUser", "Test")
    page.wait_for_load_state("networkidle")

    # Go offline
    page.context.set_offline(True)
    page.reload()
    page.wait_for_load_state("domcontentloaded")

    assignment = page.locator("[data-testid='assignment']").or_(
        page.get_by_text("gifting", exact=False)
    )
    assert assignment.is_visible(timeout=5000), \
        "Assignment should still be visible when offline (served from cache)"

    # Restore network
    page.context.set_offline(False)


# 18. Register while offline — error or queue, no silent data loss
def test_register_offline_shows_error(page):
    page.context.set_offline(True)
    page.reload()
    page.wait_for_load_state("domcontentloaded")

    page.get_by_label("First name", exact=False).fill("OfflineReg")
    page.get_by_label("Last name", exact=False).fill("Test")
    page.get_by_role("button", name="Register").or_(
        page.get_by_role("button", name="Confirm")
    ).click()
    page.wait_for_timeout(2000)

    error = page.locator("[role='alert'], [data-testid='error']")
    queued = page.get_by_text("queue", exact=False)
    assert error.is_visible() or queued.is_visible(), \
        "Registering while offline should show an error or queue the action — not silently lose data"

    page.context.set_offline(False)
