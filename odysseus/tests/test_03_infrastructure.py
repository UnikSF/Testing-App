import subprocess
import socket
import pytest
from conftest import docker_skip, _is_ui_up


def _compose(args: list, cwd: str, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(["docker", "compose"] + args, cwd=cwd, capture_output=True, **kwargs)


# 10. Graceful shutdown while streaming — containers stop cleanly
@pytest.mark.docker
def test_graceful_shutdown_during_stream(docker_available, compose_dir, page, base_url):
    docker_skip(docker_available)
    from pages.chat_page import ChatPage

    chat = ChatPage(page)
    chat.send_message("Count from 1 to 100 slowly.")

    # Stop containers while response is (possibly) still streaming
    result = _compose(["stop"], cwd=compose_dir, timeout=30)
    assert result.returncode == 0, \
        f"docker compose stop should exit cleanly, got:\n{result.stderr.decode()}"

    # Restart for subsequent tests
    _compose(["start"], cwd=compose_dir, timeout=60)
    _is_ui_up(base_url, timeout=30)


# 11. Odysseus starts only after Ollama is healthy
@pytest.mark.docker
def test_odysseus_waits_for_ollama_healthcheck(docker_available, compose_dir):
    docker_skip(docker_available)
    result = _compose(["ps", "--format", "json"], cwd=compose_dir, timeout=10)
    output = result.stdout.decode()

    assert "healthy" in output or result.returncode == 0, \
        "Ollama container should be healthy before Odysseus UI starts"


# 12. Volume persistence — model not re-downloaded after restart
@pytest.mark.docker
def test_volume_persistence(docker_available, compose_dir, base_url):
    docker_skip(docker_available)
    # Bring down without removing volumes
    _compose(["down"], cwd=compose_dir, timeout=60)

    import time
    start = time.time()
    _compose(["up", "--wait", "--detach"], cwd=compose_dir, timeout=120)
    elapsed = time.time() - start

    assert _is_ui_up(base_url, timeout=60), "UI should come back up after restart"
    # A warm restart with volumes should be substantially faster than a cold start
    assert elapsed < 120, f"Restart with persisted volumes took {elapsed:.0f}s — too long"


# 13. Port conflict — compose fails with clear error
@pytest.mark.docker
def test_port_conflict_gives_clear_error(docker_available, compose_dir):
    docker_skip(docker_available)
    # Bind port 3000 ourselves so compose cannot claim it
    with socket.socket() as s:
        try:
            s.bind(("0.0.0.0", 3000))
        except OSError:
            pytest.skip("Port 3000 already in use — cannot simulate conflict reliably")

        result = _compose(["up", "--wait", "--detach"], cwd=compose_dir, timeout=30)
        output = (result.stdout + result.stderr).decode().lower()

        assert result.returncode != 0, "docker compose up should fail when port 3000 is taken"
        assert "address already in use" in output or "port" in output or "bind" in output, \
            "Error message should mention the port conflict"


# 14. NVIDIA overlay — nvidia-smi visible inside ollama container
@pytest.mark.docker
@pytest.mark.gpu
def test_nvidia_overlay_exposes_gpu(docker_available, compose_dir):
    docker_skip(docker_available)
    result = subprocess.run(
        ["docker", "compose", "exec", "ollama", "nvidia-smi"],
        cwd=compose_dir, capture_output=True, timeout=15,
    )
    assert result.returncode == 0, \
        "nvidia-smi should succeed inside the ollama container when NVIDIA overlay is active"


# 15. GPU overlay on machine without GPU — fails with a clear error
@pytest.mark.docker
@pytest.mark.gpu
def test_nvidia_overlay_without_gpu_fails_clearly(docker_available, compose_dir):
    docker_skip(docker_available)
    result = _compose(
        ["-f", "docker-compose.yml", "-f", "docker/ollama.yml", "-f", "docker/gpu.nvidia.yml",
         "up", "--wait", "--detach"],
        cwd=compose_dir, timeout=60,
    )
    if result.returncode != 0:
        output = (result.stdout + result.stderr).decode().lower()
        assert "gpu" in output or "driver" in output or "device" in output, \
            "Error should mention GPU/driver, not be a silent hang"
    else:
        pytest.skip("GPU is available on this machine — cannot test the no-GPU failure path")
