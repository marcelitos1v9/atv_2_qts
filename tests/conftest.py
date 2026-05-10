import pytest

from app import create_app, services


@pytest.fixture
def app():
    return create_app(testing=True)


@pytest.fixture
def client(app):
    services.reset_store()
    return app.test_client()


@pytest.fixture
def sample_book(client):
    response = client.post(
        "/books",
        json={"title": "Clean Code", "author": "Robert Martin", "year": 2008},
    )
    return response.get_json()
