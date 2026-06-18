import subprocess
import time
import requests
import pytest
from conftest import docker_skip, _is_ui_up


# 1. Fresh start — images pull, model downloads, UI accessible within ~5 min
@pytest.mark.docker
def test_fresh_start_ui_accessible(docker_available, compose_dir, base_url):
    docker_skip(docker_available)
    subprocess.run(["docker", "compose", "down", "-v"], cwd=compose_dir, check=False)
    proc = subprocess.Popen(
        ["docker", "compose", "up", "--wait"],
        cwd=compose_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        assert _is_ui_up(base_url, timeout=300), \
            "UI should be accessible within 5 minutes of fresh docker compose up"
    finally:
        proc.terminate()
        proc.wait(timeout=30)


# 2. Warm start — UI available quickly, model pull is a no-op
@pytest.mark.docker
def test_warm_start_is_fast(docker_available, compose_dir, base_url):
    docker_skip(docker_available)
    start = time.time()
    subprocess.run(
        ["docker", "compose", "up", "--wait", "--detach"],
        cwd=compose_dir, check=True, timeout=60,
    )
    elapsed = time.time() - start
    assert _is_ui_up(base_url, timeout=30), "UI should be up within 30 s on warm start"
    assert elapsed < 30, f"Warm start took {elapsed:.1f}s — expected under 30 s"


# 3. Wrong OLLAMA_PULL_MODELS — error in logs, no silent hang
@pytest.mark.docker
def test_bad_model_name_shows_error_in_logs(docker_available, compose_dir):
    docker_skip(docker_available)
    env_override = {"OLLAMA_PULL_MODELS": "doesnotexist:latest"}
    proc = subprocess.run(
        ["docker", "compose", "up", "--abort-on-container-exit"],
        cwd=compose_dir,
        env={**__import__("os").environ, **env_override},
        capture_output=True,
        timeout=120,
    )
    combined = (proc.stdout + proc.stderr).decode()
    assert "error" in combined.lower() or "not found" in combined.lower(), \
        "Bad model name should produce an error in logs, not hang silently"


# 4. COMPOSE_FILE not set — starts but reports no models
@pytest.mark.docker
def test_no_compose_file_shows_no_models(docker_available, compose_dir, page):
    docker_skip(docker_available)
    # This test assumes Odysseus UI is already running without Ollama
    from pages.chat_page import ChatPage
    chat = ChatPage(page)
    # Either models are unavailable or there is a connection error message
    assert chat.is_no_models_shown() or len(chat.get_available_models()) == 0, \
        "Without Ollama sidecar, UI should report no models or connection error"
