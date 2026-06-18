import pytest
from playwright.sync_api import sync_playwright


def pytest_addoption(parser):
    parser.addoption("--base-url", default="http://localhost:3000", help="Finance Watcher base URL")
    parser.addoption("--headed", action="store_true", default=False, help="Run browser in headed mode")
    parser.addoption("--slow-mo", type=int, default=0, help="Slow down Playwright actions (ms)")


@pytest.fixture(scope="session")
def browser(request):
    headed = request.config.getoption("--headed")
    slow_mo = request.config.getoption("--slow-mo")
    with sync_playwright() as p:
        b = p.chromium.launch(headless=not headed, slow_mo=slow_mo)
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
