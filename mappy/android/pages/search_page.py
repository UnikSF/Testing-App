# Element IDs to verify with Appium Inspector against the real Mappy app build.
from appium.webdriver.common.appiumby import AppiumBy
from .base_page import BasePage

SEARCH_INPUT    = (AppiumBy.ID, "com.mappy.app:id/search_input")
FILTER_OPEN_NOW = (AppiumBy.XPATH, '//*[@text="Ouvert maintenant"]')
RESULT_ITEM     = (AppiumBy.XPATH, '//android.widget.RecyclerView/android.view.ViewGroup')
NO_RESULTS_MSG  = (AppiumBy.XPATH, '//*[@text="Aucun résultat"]')


class SearchPage(BasePage):
    def search(self, query: str):
        self.type_text(SEARCH_INPUT, query)
        self.driver.press_keycode(66)  # KEYCODE_ENTER

    def apply_filter_open_now(self):
        self.tap(FILTER_OPEN_NOW)

    def get_results(self):
        return self.find_all(RESULT_ITEM)

    def select_first_result(self):
        results = self.get_results()
        assert results, "Aucun résultat de recherche trouvé"
        results[0].click()

    def has_no_results(self):
        return self.is_visible(NO_RESULTS_MSG, timeout=5)
