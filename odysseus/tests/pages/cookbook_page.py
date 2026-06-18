# Cookbook = model download + serve flow in the real Odysseus workspace.
# Download puts files on disk; Serve launches a backend (Ollama / llama.cpp)
# and registers a ModelEndpoint so the model appears in the chat picker.
from playwright.sync_api import Page
from .base_page import BasePage


class CookbookPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.model_search = page.get_by_placeholder("Search models", exact=False).or_(
            page.get_by_role("searchbox")
        )
        self.download_buttons = page.get_by_role("button", name="Download")
        self.serve_buttons = page.get_by_role("button", name="Serve")
        self.ollama_models = page.locator("[data-ollama='true'], [data-testid='ollama-model']")
        self.download_progress = page.locator("[role='progressbar'], .progress-bar")
        self.serve_status = page.locator("[data-testid='serve-status'], .serve-status")

    def navigate(self):
        self.page.get_by_role("link", name="Cookbook").or_(
            self.page.get_by_role("link", name="Models")
        ).click()
        self.page.wait_for_load_state("networkidle")

    def get_listed_model_count(self) -> int:
        return self.page.locator("[data-testid='model-card'], .model-card, .model-item").count()

    def serve_first_ollama_model(self):
        serve = self.serve_buttons.first
        assert serve.is_visible(), "No Serve button visible — is Ollama running?"
        serve.click()
        self.page.wait_for_load_state("networkidle")

    def is_download_in_progress(self) -> bool:
        return self.is_visible(self.download_progress)

    def get_serve_status_text(self) -> str:
        if self.is_visible(self.serve_status, timeout=3000):
            return self.get_text(self.serve_status)
        return ""
