# Testing App — Project Index

Central reference for all personal projects. Each folder contains a README (setup + description) and a test scenarios file.

| Project | App status | Tests |
|---|---|---|
| Mappy | Done | [mappy/android/](mappy/android/) — pytest + Appium (28 tests) |
| Odysseus for Docker | Done | [odysseus/tests/](odysseus/tests/) — pytest + Playwright + Docker (15 tests) |
| Finance Watcher | In progress | [finance-watcher/](finance-watcher/) — pytest + Playwright (21 tests) |
| Matrix Planning | Not started | [matrix-planning/tests/](matrix-planning/tests/) — pytest + Playwright (14 tests) |
| Mystery Santa | Not started | [mystery-santa/tests/](mystery-santa/tests/) — pytest + Playwright (18 tests) |

## How to run tests

Each project has its own `requirements.txt`. Install and run from the project's test folder:

```bash
pip install -r requirements.txt
playwright install chromium   # first time only (web projects)

# Mappy Android (requires Appium server + emulator)
cd mappy/android
pytest --device emulator-5554 --appium-url http://127.0.0.1:4723

# Odysseus (requires docker compose up in odysseus/)
cd odysseus/tests
pytest -m "not docker"        # UI-only tests
pytest                        # all tests (Docker must be running)

# Finance Watcher (requires npm run dev in the app folder)
cd finance-watcher
pytest

# Matrix Planning / Mystery Santa (app not built yet — tests define expected behaviour)
cd matrix-planning/tests
pytest
```
