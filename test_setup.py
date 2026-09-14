"""
Quick sanity check that Day 3 dependencies are installed and usable.

Run it with the venv's interpreter, e.g.:
    ./venv/Scripts/python.exe test_setup.py
or, with pytest installed:
    ./venv/Scripts/python.exe -m pytest test_setup.py -v
"""

import sys
from importlib.metadata import version


def test_requests_import():
    import requests
    assert hasattr(requests, "get")
    print(f"requests {version('requests')} OK")


def test_flask_import():
    import flask
    assert hasattr(flask, "Flask")
    print(f"flask {version('flask')} OK")


def test_flask_restful_import():
    import flask_restful
    assert hasattr(flask_restful, "Api")
    assert hasattr(flask_restful, "Resource")
    print(f"flask_restful {version('flask-restful')} OK")


def test_minimal_flask_restful_app():
    """Build a tiny API and hit it with the Flask test client end-to-end."""
    from flask import Flask
    from flask_restful import Api, Resource

    app = Flask(__name__)
    api = Api(app)

    class Ping(Resource):
        def get(self):
            return {"status": "ok"}

    api.add_resource(Ping, "/ping")

    client = app.test_client()
    response = client.get("/ping")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
    print("flask + flask_restful request/response cycle OK")


if __name__ == "__main__":
    tests = [
        test_requests_import,
        test_flask_import,
        test_flask_restful_import,
        test_minimal_flask_restful_app,
    ]
    failures = 0
    for test in tests:
        try:
            test()
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"FAILED: {test.__name__}: {exc}")

    if failures:
        print(f"\n{failures} test(s) failed.")
        sys.exit(1)
    else:
        print(f"\nAll {len(tests)} tests passed. Environment is ready.")
