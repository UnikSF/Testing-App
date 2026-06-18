import pytest
from pages.home_page import HomePage
from pages.search_page import SearchPage
from pages.route_options_page import RouteOptionsPage
from fixtures.locations import HOME


@pytest.fixture(autouse=True)
def reset_position(driver):
    driver.set_location(HOME["lat"], HOME["lng"], 0)
    driver.activate_app("com.mappy.app")


def test_route_france_to_belgium(driver):
    HomePage(driver).tap_search_bar()
    search = SearchPage(driver)
    search.search("Bruxelles, Belgique")
    search.select_first_result()

    assert RouteOptionsPage(driver).get_distance(), \
        "Aucun itinéraire transfrontalier France → Belgique calculé"


def test_route_france_to_uk(driver):
    HomePage(driver).tap_search_bar()
    search = SearchPage(driver)
    search.search("Londres, Royaume-Uni")
    search.select_first_result()

    assert RouteOptionsPage(driver).get_distance(), \
        "Aucun itinéraire transfrontalier France → Royaume-Uni calculé"


def test_cross_country_offers_at_least_one_route(driver):
    HomePage(driver).tap_search_bar()
    search = SearchPage(driver)
    search.search("Berlin, Allemagne")
    search.select_first_result()

    count = RouteOptionsPage(driver).get_route_options_count()
    assert count >= 1, "Aucune option de route pour une destination internationale (Berlin)"
