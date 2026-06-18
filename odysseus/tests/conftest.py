import subprocess
import time
import pytest
import requests
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:3000"
COMPOSE_DIR = ".."  # odysseus/ root where docker-compose.yml lives


def pytest_addoption(parser):
    parser.addoption("--base-url", default=BASE_URL, help="Odysseus UI base URL")
    parser.addoption("--headed", action="store_true", default=False)
    parser.addoption("--compose-dir", default=COMPOSE_DIR, help="Directory containing docker-compose.yml")


def _is_ui_up(url: str, timeout: int = 30) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = requests.get(url, timeout=3)
            if resp.status_code < 500:
                return True
        except Exception:
            pass
        time.sleep(2)
    return False


@pytest.fixture(scope="session")
def base_url(request) -> str:
    return request.config.getoption("--base-url")


@pytest.fixture(scope="session")
def compose_dir(request) -> str:
    return request.config.getoption("--compose-dir")


@pytest.fixture(scope="session")
def browser(request):
    headed = request.config.getoption("--headed")
    with sync_playwright() as p:
        b = p.chromium.launch(headless=not headed)
        yield b
        b.close()


@pytest.fixture
def page(browser, base_url):
    ctx = browser.new_context(base_url=base_url)
    pg = ctx.new_page()
    pg.goto("/")
    pg.wait_for_load_state("networkidle")
    yield pg
    ctx.close()


@pytest.fixture(scope="session")
def docker_available() -> bool:
    try:
        result = subprocess.run(
            ["docker", "info"], capture_output=True, timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def docker_skip(docker_available):
    if not docker_available:
        pytest.skip("Docker not available — skipping container test")
