import pytest
from pages.home_page import HomePage
from pages.return_home_page import ReturnHomePage
from fixtures.locations import HOME, EPICERIE


def test_return_home_from_grocery_shows_route(driver):
    driver.set_location(EPICERIE["lat"], EPICERIE["lng"], 0)
    driver.activate_app("com.mappy.app")

    HomePage(driver).tap_return_home()

    assert ReturnHomePage(driver).is_route_to_home_displayed(), \
        "L'itinéraire retour domicile n'est pas affiché depuis l'épicerie"


def test_return_home_without_home_configured_shows_prompt(driver):
    # Requires home address NOT set in the app; run after clearing app data or on a fresh account.
    driver.set_location(EPICERIE["lat"], EPICERIE["lng"], 0)
    driver.activate_app("com.mappy.app")

    HomePage(driver).tap_return_home()

    assert ReturnHomePage(driver).is_configure_home_prompt_visible(), \
        "L'invite de configuration du domicile devrait s'afficher si aucun domicile n'est enregistré"


def test_return_home_when_already_at_home(driver):
    driver.set_location(HOME["lat"], HOME["lng"], 0)
    driver.activate_app("com.mappy.app")

    HomePage(driver).tap_return_home()

    page = ReturnHomePage(driver)
    assert page.is_already_home_message_visible() or page.is_route_to_home_displayed(), \
        "Comportement inattendu quand la position GPS correspond au domicile"
