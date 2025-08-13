Testing framework and library: pytest with fastapi.testclient.TestClient (Starlette's TestClient).
These tests validate:
- Root endpoint returns expected HTML and headers
- Static files mount behavior conditional on "static" directory presence
- Basic HTTP method behaviors (HEAD, POST 405)
- Import safety with __main__ guard

If your project uses a different testing framework, update the tests accordingly.