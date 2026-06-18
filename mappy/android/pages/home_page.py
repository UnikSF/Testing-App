# Element IDs to verify with Appium Inspector against the real Mappy app build.
from appium.webdriver.common.appiumby import AppiumBy
from .base_page import BasePage

SEARCH_BAR      = (AppiumBy.ID, "com.mappy.app:id/search_input")
RETURN_HOME_BTN = (AppiumBy.XPATH, '//*[@text="Rentrer chez moi" or @text="Retour domicile"]')
MAP_VIEW        = (AppiumBy.ID, "com.mappy.app:id/map_view")


class HomePage(BasePage):
    def tap_search_bar(self):
        self.tap(SEARCH_BAR)

    def tap_return_home(self):
        self.tap(RETURN_HOME_BTN)

    def is_map_displayed(self):
        return self.is_visible(MAP_VIEW)
