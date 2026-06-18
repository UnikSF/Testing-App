# Element IDs to verify with Appium Inspector against the real Mappy app build.
from appium.webdriver.common.appiumby import AppiumBy
from .base_page import BasePage

ITINERARY_BTN = (AppiumBy.XPATH, '//*[@text="Itinéraire" or @text="Y aller"]')
FAVORITE_BTN  = (AppiumBy.ACCESSIBILITY_ID, "Ajouter aux favoris")
POI_NAME      = (AppiumBy.ID, "com.mappy.app:id/poi_name")
OPEN_STATUS   = (AppiumBy.XPATH, '//*[@text="Ouvert" or @text="Fermé"]')


class PoiDetailPage(BasePage):
    def get_poi_name(self) -> str:
        return self.get_text(POI_NAME)

    def get_open_status(self) -> str:
        return self.get_text(OPEN_STATUS)

    def tap_itinerary(self):
        self.tap(ITINERARY_BTN)

    def tap_favorite(self):
        self.tap(FAVORITE_BTN)

    def is_open(self) -> bool:
        return "Ouvert" in self.get_open_status()
