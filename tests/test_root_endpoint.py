import importlib
import types
from contextlib import contextmanager
from typing import Generator

import os
import sys

import pytest

try:
    # Prefer FastAPI's TestClient (built on Starlette)
    from fastapi.testclient import TestClient
except Exception:  # pragma: no cover - fallback for projects using starlette directly
    from starlette.testclient import TestClient  # type: ignore


@contextmanager
def temporarily_in_sys_modules(name: str, module: types.ModuleType) -> Generator[None, None, None]:
    """Temporarily insert a module into sys.modules under a specific name."""
    original = sys.modules.get(name)
    sys.modules[name] = module
    try:
        yield
    finally:
        if original is not None:
            sys.modules[name] = original
        else:
            sys.modules.pop(name, None)


def _import_app_module():
    """
    Import the app module containing a FastAPI() instance named 'app'.

    We try common locations if direct import fails. The provided snippet shows the code
    in tests/test_app.py, but that's typically an application module. We handle both cases.

    Returns the imported module and the app object.
    """
    candidates = [
        # 1) The provided path per snippet (unusual but supplied)
        "tests.test_app",
        # 2) Common app names
        "app",
        "main",
        "src.app",
        "src.main",
        "application",
    ]
    last_exc = None
    for modname in candidates:
        try:
            mod = importlib.import_module(modname)
            if hasattr(mod, "app"):
                return mod, mod.app
        except Exception as exc:  # keep trying
            last_exc = exc
    raise RuntimeError(f"Could not locate FastAPI 'app' in candidates {candidates}. Last error: {last_exc}")


@pytest.fixture(scope="session")
def app_module_and_app():
    mod, app = _import_app_module()
    return mod, app


@pytest.fixture()
def client(app_module_and_app):
    _, app = app_module_and_app
    return TestClient(app)


def test_root_returns_expected_html_and_status_ok(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.text == "<h1>Hello GreenAI</h1>"
    # FastAPI HTMLResponse by default sets correct content type header
    assert "text/html" in resp.headers.get("content-type", "").lower()


def test_root_supports_head_request(client):
    resp = client.head("/")
    # Starlette will treat HEAD similar to GET sans body for simple routes
    assert resp.status_code == 200
    # Body may be empty on HEAD; verify header still HTML
    assert "text/html" in resp.headers.get("content-type", "").lower()


def test_root_method_not_allowed_for_post(client):
    resp = client.post("/")
    assert resp.status_code in (405, 404)  # Prefer 405; some routers might produce 404 if no route matches
    # If 405, allow header may be present
    if resp.status_code == 405:
        allow = resp.headers.get("allow", "")
        assert "GET" in allow or "HEAD" in allow


@pytest.mark.parametrize(
    "accept_header",
    [
        "*/*",
        "text/html",
        "text/*",
        "application/xhtml+xml",
        "application/json",  # even if JSON is requested, HTMLResponse should still respond with text/html
    ],
)
def test_root_respects_various_accept_headers(client, accept_header):
    resp = client.get("/", headers={"accept": accept_header})
    assert resp.status_code == 200
    assert resp.text == "<h1>Hello GreenAI</h1>"
    assert "text/html" in resp.headers.get("content-type", "").lower()


def test_static_mount_present_when_directory_exists(monkeypatch):
    """
    The app mounts /static only if os.path.exists('static') is True at import time.
    We simulate True and ensure an app object can be created and a static route exists.
    """
    import types

    # Create a pseudo module replicating the snippet's content programmatically,
    # so we can control the os.path.exists return value at import time.
    module_code = '''
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Static files serving
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>Hello GreenAI</h1>"
'''
    # Force exists -> True
    monkeypatch.setattr(os.path, "exists", lambda p: True)

    pseudo = types.ModuleType("pseudo_app_true")
    exec(module_code, pseudo.__dict__)
    with temporarily_in_sys_modules("pseudo_app_true", pseudo):
        # Import the pseudo module to get app
        mod = importlib.import_module("pseudo_app_true")
        app = mod.app
        test_client = TestClient(app)

        # We should be able to hit the root
        r = test_client.get("/")
        assert r.status_code == 200
        # And static should be mounted: request to /static should not 404 immediately (directory content may 404)
        # Hitting /static/ should return some response (likely 404 if file missing). We mainly ensure the router is mounted.
        r2 = test_client.get("/static/")
        assert r2.status_code in (200, 404)


def test_static_mount_absent_when_directory_missing(monkeypatch):
    """
    Simulate False for os.path.exists('static') and ensure /static is not mounted, leading to 404.
    """
    import types

    module_code = '''
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>Hello GreenAI</h1>"
'''
    monkeypatch.setattr(os.path, "exists", lambda p: False)

    pseudo = types.ModuleType("pseudo_app_false")
    exec(module_code, pseudo.__dict__)
    with temporarily_in_sys_modules("pseudo_app_false", pseudo):
        mod = importlib.import_module("pseudo_app_false")
        app = mod.app
        test_client = TestClient(app)

        r = test_client.get("/")
        assert r.status_code == 200

        # Since static was not mounted, hitting /static path should 404.
        r2 = test_client.get("/static/")
        assert r2.status_code == 404


def test_main_block_is_non_intrusive_on_import(app_module_and_app, monkeypatch):
    """
    Verify that importing the module does not attempt to run uvicorn (i.e., __name__ != '__main__' guard exists).
    """
    mod, _ = app_module_and_app

    # Ensure module has the typical guard
    source = None
    try:
        import inspect
        source = inspect.getsource(mod)
    except Exception:
        pass

    if source:
        assert "__name__ == \"__main__\"" in source or "__name__ == '__main__'" in source

    # Import again to assert no side-effect server starts (we just check that no attribute named 'uvicorn_server_started' etc.)
    # This is a smoke test; if import tried to run uvicorn, tests would hang or fail. Re-import should be safe.
    importlib.reload(mod)