"""Shared fixtures: serve the repo over a local HTTP server and replace the
Mermaid CDN script with a deterministic fake (no network access in tests)."""

import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Fake mermaid: records initialize() config and render() calls. Code containing
# "INVALID" throws an Error, "THROWSTRING" throws a bare string.
FAKE_MERMAID_JS = r"""
window.__mermaid = { initConfig: null, calls: [] };
window.mermaid = {
  initialize(cfg) { window.__mermaid.initConfig = cfg; },
  async render(id, code) {
    window.__mermaid.calls.push({ id, code });
    if (code.includes('THROWSTRING')) { throw 'bare string failure'; }
    if (code.includes('INVALID')) {
      throw new Error('Parse error on line 2: INVALID token');
    }
    const esc = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return {
      svg: '<svg xmlns="http://www.w3.org/2000/svg" id="' + id +
           '" width="200" height="100"><text x="10" y="20">' + esc + '</text></svg>'
    };
  }
};
"""

CLIPBOARD_STUB_JS = r"""
window.__copied = null;
Object.defineProperty(navigator, 'clipboard', {
  configurable: true,
  value: { writeText: async (t) => { window.__copied = t; } },
});
"""


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def server_url():
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=str(REPO_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    deadline = time.time() + 15
    while True:
        try:
            urllib.request.urlopen(base + "/index.html", timeout=1).close()
            break
        except Exception:
            if proc.poll() is not None or time.time() > deadline:
                proc.kill()
                raise RuntimeError("http.server failed to start")
            time.sleep(0.1)
    yield base
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture
def app(page, server_url):
    """Open index.html with fake mermaid + stubbed clipboard; wait for first render."""

    def handler(route):
        url = route.request.url
        if "mermaid" in url and "cdn.jsdelivr.net" in url:
            route.fulfill(status=200, content_type="application/javascript", body=FAKE_MERMAID_JS)
        elif url.startswith(server_url):
            route.continue_()
        else:
            route.abort()

    page.route("**/*", handler)
    page.add_init_script(CLIPBOARD_STUB_JS)
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(server_url + "/index.html")
    page.wait_for_function("() => window.__mermaid && window.__mermaid.calls.length >= 1")
    page.wait_for_function("() => document.getElementById('status').textContent === 'Rendered OK'")
    return page
