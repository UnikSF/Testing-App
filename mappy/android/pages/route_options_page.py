# Element IDs to verify with Appium Inspector against the real Mappy app build.
from appium.webdriver.common.appiumby import AppiumBy
from .base_page import BasePage

FASTEST_ROUTE    = (AppiumBy.XPATH, '//*[@text="Le plus rapide" or @text="Rapide"]')
ECO_ROUTE        = (AppiumBy.XPATH, '//*[@text="Éco" or @text="Économique"]')
NO_TOLL_ROUTE    = (AppiumBy.XPATH, '//*[@text="Sans péage"]')
TOLL_PRICE       = (AppiumBy.ID, "com.mappy.app:id/toll_price")
START_NAV_BTN    = (AppiumBy.XPATH, '//*[@text="Démarrer" or @text="Go"]')
ROUTE_DISTANCE   = (AppiumBy.ID, "com.mappy.app:id/route_distance")
ROUTE_OPTION_CARD = (AppiumBy.ID, "com.mappy.app:id/route_option_card")


class RouteOptionsPage(BasePage):
    def select_fastest_route(self):
        self.tap(FASTEST_ROUTE)

    def select_eco_route(self):
        self.tap(ECO_ROUTE)

    def select_no_toll_route(self):
        self.tap(NO_TOLL_ROUTE)

    def get_toll_price(self) -> str | None:
        if self.is_visible(TOLL_PRICE, timeout=5):
            return self.get_text(TOLL_PRICE)
        return None

    def start_navigation(self):
        self.tap(START_NAV_BTN)

    def get_route_options_count(self) -> int:
        return len(self.find_all(ROUTE_OPTION_CARD))

    def get_distance(self) -> str:
        return self.get_text(ROUTE_DISTANCE)
