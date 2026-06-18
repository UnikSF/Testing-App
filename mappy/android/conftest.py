import pytest
from appium import webdriver
from appium.options import UiAutomator2Options
from fixtures.locations import HOME


def pytest_addoption(parser):
    parser.addoption("--device", default="emulator-5554", help="Android device name or emulator ID")
    parser.addoption("--apk", default=None, help="Path to Mappy APK (optional if already installed)")
    parser.addoption("--appium-url", default="http://127.0.0.1:4723", help="Appium server URL")


@pytest.fixture(scope="session")
def driver(request):
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = request.config.getoption("--device")
    options.app_package = "com.mappy.app"
    options.app_activity = ".ui.MainActivity"
    options.automation_name = "UiAutomator2"
    options.no_reset = True
    options.new_command_timeout = 120

    apk = request.config.getoption("--apk")
    if apk:
        options.app = apk

    drv = webdriver.Remote(
        request.config.getoption("--appium-url"),
        options=options,
    )
    drv.implicitly_wait(10)
    drv.set_location(HOME["lat"], HOME["lng"], 0)

    yield drv
    drv.quit()
