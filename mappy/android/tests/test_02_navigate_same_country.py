import pytest
from pages.home_page import HomePage
from pages.search_page import SearchPage
from pages.route_options_page import RouteOptionsPage
from pages.navigation_page import NavigationPage
from fixtures.locations import HOME


@pytest.fixture(autouse=True)
def reset_position(driver):
    driver.set_location(HOME["lat"], HOME["lng"], 0)
    driver.activate_app("com.mappy.app")


def test_route_to_paris_address(driver):
    HomePage(driver).tap_search_bar()
    search = SearchPage(driver)
    search.search("Rue de Rivoli, Paris")
    search.select_first_result()

    assert RouteOptionsPage(driver).get_distance(), "Aucune distance affichée pour l'itinéraire"


def test_route_shows_multiple_options(driver):
    HomePage(driver).tap_search_bar()
    search = SearchPage(driver)
    search.search("Lyon Part-Dieu")
    search.select_first_result()

    count = RouteOptionsPage(driver).get_route_options_count()
    assert count >= 2, f"Moins de 2 options de route affichées ({count})"


def test_eco_route_shows_toll_price(driver):
    HomePage(driver).tap_search_bar()
    search = SearchPage(driver)
    search.search("Marseille Saint-Charles")
    search.select_first_result()

    route = RouteOptionsPage(driver)
    route.select_eco_route()

    assert route.get_toll_price() is not None, "Prix de péage non affiché pour la route éco"


def test_navigation_starts_with_instructions(driver):
    HomePage(driver).tap_search_bar()
    search = SearchPage(driver)
    search.search("Rue de Rivoli, Paris")
    search.select_first_result()

    route = RouteOptionsPage(driver)
    route.select_fastest_route()
    route.start_navigation()

    nav = NavigationPage(driver)
    assert nav.is_navigating(), "La navigation n'a pas démarré"
    assert nav.get_current_instruction(), "Aucune instruction de navigation affichée"

    nav.exit_navigation()
