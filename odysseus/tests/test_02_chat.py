import pytest
from pages.chat_page import ChatPage

# Real Odysseus is a FastAPI workspace; Chat is one of its modules.
# Models appear in the picker only when their backend server (Ollama / llama.cpp) is running
# AND registered as a ModelEndpoint in the DB. Tests assume at least one model is served.


@pytest.fixture(autouse=True)
def fresh_chat(page):
    ChatPage(page).start_new_chat()


# 5. Send a simple message — model responds correctly
def test_simple_message_gets_response(page):
    chat = ChatPage(page)
    count_before = chat.get_message_count()

    chat.send_message("What is 2 + 2?")
    chat.wait_for_response()

    response = chat.get_last_message()
    assert "4" in response, f"Expected '4' in response to '2 + 2', got: '{response}'"
    assert chat.get_message_count() > count_before, "Response message should appear"


# 6. Multi-turn conversation — model maintains context across turns
def test_multi_turn_context(page):
    chat = ChatPage(page)

    chat.send_message("My name is Alexandre.")
    chat.wait_for_response()

    chat.send_message("What is my name?")
    chat.wait_for_response()

    chat.send_message("Repeat my name one more time, please.")
    chat.wait_for_response()

    last = chat.get_last_message().lower()
    assert "alexandre" in last, \
        f"Model should recall the name from context, got: '{last}'"


# 7. Long input — no timeout or truncation
def test_long_input_handled(page):
    long_text = "Paris est la capitale de la France. " * 60
    question = f"{long_text}\n\nIn one word: what city is described above?"

    chat = ChatPage(page)
    chat.send_message(question)
    chat.wait_for_response(timeout=60000)

    response = chat.get_last_message()
    assert "paris" in response.lower(), \
        f"Model should answer 'Paris' for the long-context question, got: '{response}'"


# 8. Empty message — UI does not crash, message not sent
def test_empty_message_does_not_crash(page):
    chat = ChatPage(page)
    count_before = chat.get_message_count()

    chat.message_input.fill("")
    chat.message_input.press("Enter")
    page.wait_for_timeout(1000)

    assert not page.is_closed(), "Page should not crash"
    assert chat.get_message_count() == count_before, \
        "Empty message should not be sent"


# 9. Model picker — shows only models whose backend is running (registered ModelEndpoints)
def test_model_picker_shows_served_models(page):
    chat = ChatPage(page)
    models = chat.get_available_models()

    assert len(models) >= 1, \
        "At least one model should be in the picker — is any backend (Ollama/llama.cpp) running?"


def test_model_switching_works(page):
    chat = ChatPage(page)
    models = chat.get_available_models()

    if len(models) < 2:
        pytest.skip("Need at least 2 served models to test switching")

    chat.select_model(models[1])
    chat.send_message("Hello")
    chat.wait_for_response()

    assert len(chat.get_last_message()) > 0, \
        f"Model '{models[1]}' should respond after switching"

    chat.select_model(models[0])


# Extra: model picker empty when no backend is running
def test_model_picker_empty_when_no_backend(page):
    chat = ChatPage(page)
    models = chat.get_available_models()

    if len(models) > 0:
        pytest.skip("Backend is running — cannot test the no-backend empty state")

    assert chat.is_no_models_shown() or len(models) == 0, \
        "No models should appear when no backend server is registered"
