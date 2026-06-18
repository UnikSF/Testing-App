# Selectors based on the real Odysseus FastAPI workspace UI.
# Verify with browser DevTools against the running app and adjust as needed.
from playwright.sync_api import Page
from .base_page import BasePage


class ChatPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.message_input = page.get_by_role("textbox").or_(
            page.locator("textarea[placeholder*='message'], textarea[placeholder*='chat'], [contenteditable='true']")
        )
        self.send_btn = page.get_by_role("button", name="Send").or_(
            page.locator("button[type='submit'], button[aria-label*='send'], button[aria-label*='Send']")
        )
        self.chat_messages = page.locator(
            "[data-testid='message'], .message, .chat-message, [class*='message-content']"
        )
        self.model_selector = page.get_by_role("combobox").or_(
            page.locator("select[name*='model'], [data-testid='model-select'], .model-picker")
        )
        self.no_models_msg = page.get_by_text("no model", exact=False).or_(
            page.get_by_text("unavailable", exact=False)
        )
        self.new_chat_btn = page.get_by_role("button", name="New chat").or_(
            page.get_by_role("link", name="New chat").or_(
                page.get_by_title("New chat")
            )
        )

    def send_message(self, text: str):
        self.message_input.click()
        self.message_input.fill(text)
        self.send_btn.click()

    def wait_for_response(self, timeout: int = 30000):
        loading = self.page.locator(
            "[data-testid='loading'], .loading, [aria-busy='true'], .thinking, .generating"
        )
        try:
            loading.wait_for(state="attached", timeout=3000)
            loading.wait_for(state="detached", timeout=timeout)
        except Exception:
            pass
        self.page.wait_for_load_state("networkidle", timeout=timeout)

    def get_all_messages(self) -> list[str]:
        return [msg.inner_text() for msg in self.chat_messages.all()]

    def get_last_message(self) -> str:
        msgs = self.chat_messages.all()
        return msgs[-1].inner_text() if msgs else ""

    def get_message_count(self) -> int:
        return self.chat_messages.count()

    def get_available_models(self) -> list[str]:
        options = self.model_selector.locator("option").all()
        if options:
            return [opt.inner_text() for opt in options]
        # combobox pattern: click to open, read items
        try:
            self.model_selector.click()
            items = self.page.get_by_role("option").all()
            texts = [i.inner_text() for i in items]
            self.page.keyboard.press("Escape")
            return texts
        except Exception:
            return []

    def select_model(self, model_name: str):
        try:
            self.model_selector.select_option(label=model_name)
        except Exception:
            self.model_selector.click()
            self.page.get_by_role("option", name=model_name).click()

    def start_new_chat(self):
        if self.new_chat_btn.is_visible():
            self.new_chat_btn.click()
            self.page.wait_for_load_state("networkidle")

    def is_no_models_shown(self) -> bool:
        return self.is_visible(self.no_models_msg)
