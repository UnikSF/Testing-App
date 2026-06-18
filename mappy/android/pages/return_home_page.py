# Element IDs to verify with Appium Inspector against the real Mappy app build.
from appium.webdriver.common.appiumby import AppiumBy
from .base_page import BasePage

RETURN_HOME_BTN       = (AppiumBy.XPATH, '//*[@text="Rentrer chez moi" or @text="Retour domicile"]')
CONFIGURE_HOME_PROMPT = (AppiumBy.XPATH, '//*[contains(@text, "domicile") and contains(@text, "définir")]')
ALREADY_HOME_MSG      = (AppiumBy.XPATH, '//*[contains(@text, "déjà chez vous")]')
ROUTE_PREVIEW         = (AppiumBy.ID, "com.mappy.app:id/route_preview")


class ReturnHomePage(BasePage):
    def tap_return_home(self):
        self.tap(RETURN_HOME_BTN)

    def is_configure_home_prompt_visible(self) -> bool:
        return self.is_visible(CONFIGURE_HOME_PROMPT, timeout=5)

    def is_already_home_message_visible(self) -> bool:
        return self.is_visible(ALREADY_HOME_MSG, timeout=5)

    def is_route_to_home_displayed(self) -> bool:
        return self.is_visible(ROUTE_PREVIEW, timeout=10)
