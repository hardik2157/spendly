"""Browser test fixtures. Runs the Flask app on a free port and drives it with Playwright."""

import threading
from wsgiref.simple_server import make_server

import pytest

from app import app as flask_app


class _Server(threading.Thread):
    def __init__(self, application):
        super().__init__(daemon=True)
        self.server = make_server("127.0.0.1", 0, application)
        self.port = self.server.server_port

    def run(self):
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()


@pytest.fixture(scope="session")
def live_server_url():
    flask_app.config.update(TESTING=True)
    server = _Server(flask_app)
    server.start()
    yield f"http://127.0.0.1:{server.port}"
    server.stop()


@pytest.fixture(scope="session")
def browser():
    playwright_api = pytest.importorskip("playwright.sync_api")
    with playwright_api.sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    page = context.new_page()
    yield page
    context.close()
