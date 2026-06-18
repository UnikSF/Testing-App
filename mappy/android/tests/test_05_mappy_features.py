import pytest
from appium.webdriver.common.appiumby import AppiumBy
from pages.home_page import HomePage
from pages.search_page import SearchPage
from pages.poi_detail_page import PoiDetailPage
from pages.route_options_page import RouteOptionsPage
from fixtures.locations import HOME

CLUSTER_BUBBLE = (AppiumBy.ID, "com.mappy.app:id/cluster_bubble")


@pytest.fixture(autouse=True)
def reset_position(driver):
    driver.set_location(HOME["lat"], HOME["lng"], 0)
    driver.activate_app("com.mappy.app")


def _pinch_close(driver):
    size = driver.get_window_size()
    cx, cy = size["width"] // 2, size["height"] // 2
    driver.execute_script("mobile: pinchCloseGesture", {
        "left": cx - 100, "top": cy - 100,
        "width": 200, "height": 200, "percent": 0.5,
    })


def _pinch_open(driver):
    size = driver.get_window_size()
    cx, cy = size["width"] // 2, size["height"] // 2
    driver.execute_script("mobile: pinchOpenGesture", {
        "left": cx - 50, "top": cy - 50,
        "width": 100, "height": 100, "percent": 0.8,
    })


def test_clusters_visible_when_zoomed_out(driver):
    _pinch_close(driver)
    clusters = driver.find_elements(*CLUSTER_BUBBLE)
    assert len(clusters) > 0, "Aucun cluster affiché en vue dézoomée"


def test_clusters_expand_on_zoom_in(driver):
    _pinch_close(driver)
    _pinch_open(driver)
    clusters = driver.find_elements(*CLUSTER_BUBBLE)
    assert len(clusters) == 0, "Des clusters restent visibles après zoom avant"


def test_highway_route_shows_toll_price(driver):
    HomePage(driver).tap_search_bar()
    search = SearchPage(driver)
    search.search("Marseille")
    search.select_first_result()

    price = RouteOptionsPage(driver).get_toll_price()
    assert price is not None, "Le prix de péage n'est pas affiché pour un trajet avec autoroute"


def test_eco_and_standard_toll_prices_differ(driver):
    HomePage(driver).tap_search_bar()
    search = SearchPage(driver)
    search.search("Lyon")
    search.select_first_result()

    route = RouteOptionsPage(driver)
    route.select_fastest_route()
    fast_price = route.get_toll_price()

    route.select_eco_route()
    eco_price = route.get_toll_price()

    assert fast_price != eco_price, \
        "Le prix péage éco devrait être différent du prix de la route rapide"


def test_add_poi_to_favorites(driver):
    HomePage(driver).tap_search_bar()
    search = SearchPage(driver)
    search.search("Tour Eiffel")
    search.select_first_result()

    PoiDetailPage(driver).tap_favorite()

    removed_btn = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "Retirer des favoris")
    assert len(removed_btn) > 0, "Le bouton favori n'a pas basculé — lieu non ajouté aux favoris"
