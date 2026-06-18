import pytest
from pages.home_page import HomePage
from pages.search_page import SearchPage
from pages.poi_detail_page import PoiDetailPage
from pages.route_options_page import RouteOptionsPage
from fixtures.locations import HOME


@pytest.fixture(autouse=True)
def reset_position(driver):
    driver.set_location(HOME["lat"], HOME["lng"], 0)
    driver.activate_app("com.mappy.app")


def test_search_grocery_returns_results(driver):
    HomePage(driver).tap_search_bar()

    search = SearchPage(driver)
    search.search("épicerie")

    assert len(search.get_results()) > 0, "La recherche 'épicerie' ne retourne aucun résultat"


def test_filter_open_now_keeps_valid_results(driver):
    HomePage(driver).tap_search_bar()

    search = SearchPage(driver)
    search.search("épicerie")
    total = len(search.get_results())

    search.apply_filter_open_now()
    filtered = len(search.get_results())

    assert filtered <= total, "Le filtre 'ouvert maintenant' a augmenté le nombre de résultats"
    assert filtered > 0, "Aucun résultat après le filtre 'ouvert maintenant'"


def test_selected_poi_shows_name_and_open_status(driver):
    HomePage(driver).tap_search_bar()

    search = SearchPage(driver)
    search.search("épicerie")
    search.apply_filter_open_now()
    search.select_first_result()

    poi = PoiDetailPage(driver)
    assert poi.get_poi_name(), "Le nom du POI est vide"
    assert poi.is_open(), "Le POI sélectionné devrait être ouvert (filtre 'ouvert maintenant' actif)"


def test_itinerary_button_shows_route_options(driver):
    HomePage(driver).tap_search_bar()

    search = SearchPage(driver)
    search.search("épicerie")
    search.apply_filter_open_now()
    search.select_first_result()

    PoiDetailPage(driver).tap_itinerary()

    assert RouteOptionsPage(driver).get_route_options_count() > 0, \
        "Aucune option de route affichée après 'Itinéraire'"
