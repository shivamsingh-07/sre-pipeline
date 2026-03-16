"""Pytest fixtures for API tests."""

import pytest
from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    """Create app with in-memory SQLite for tests."""
    app = create_app(
        config_overrides={
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "TESTING": True,
        }
    )
    with app.app_context():
        db.create_all()
        yield app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()
