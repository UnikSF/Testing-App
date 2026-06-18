# Element IDs to verify with Appium Inspector against the real Mappy app build.
from appium.webdriver.common.appiumby import AppiumBy
from .base_page import BasePage

INSTRUCTION_BANNER = (AppiumBy.ID, "com.mappy.app:id/instruction_text")
EXIT_NAV_BTN       = (AppiumBy.ACCESSIBILITY_ID, "Quitter la navigation")
DISTANCE_TO_NEXT   = (AppiumBy.ID, "com.mappy.app:id/distance_to_maneuver")


class NavigationPage(BasePage):
    def is_navigating(self) -> bool:
        return self.is_visible(INSTRUCTION_BANNER)

    def get_current_instruction(self) -> str:
        return self.get_text(INSTRUCTION_BANNER)

    def get_distance_to_next_maneuver(self) -> str:
        return self.get_text(DISTANCE_TO_NEXT)

    def exit_navigation(self):
        self.tap(EXIT_NAV_BTN)
