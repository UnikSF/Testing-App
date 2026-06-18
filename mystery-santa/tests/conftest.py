import pytest
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:3000"


def pytest_addoption(parser):
    parser.addoption("--base-url", default=BASE_URL, help="Mystery Santa app URL")
    parser.addoption("--headed", action="store_true", default=False)


@pytest.fixture(scope="session")
def browser(request):
    headed = request.config.getoption("--headed")
    with sync_playwright() as p:
        b = p.chromium.launch(headless=not headed)
        yield b
        b.close()


@pytest.fixture
def page(browser, request):
    base_url = request.config.getoption("--base-url")
    ctx = browser.new_context(base_url=base_url)
    pg = ctx.new_page()
    pg.goto("/")
    pg.wait_for_load_state("networkidle")
    yield pg
    ctx.close()


def _register(page, first: str, last: str):
    page.get_by_label("First name", exact=False).fill(first)
    page.get_by_label("Last name", exact=False).fill(last)
    page.get_by_role("button", name="Register").or_(
        page.get_by_role("button", name="Confirm")
    ).click()
    page.wait_for_load_state("networkidle")


def _login(page, first: str, last: str):
    page.get_by_label("First name", exact=False).fill(first)
    page.get_by_label("Last name", exact=False).fill(last)
    page.get_by_role("button", name="Login").or_(
        page.get_by_role("button", name="Sign in")
    ).click()
    page.wait_for_load_state("networkidle")
