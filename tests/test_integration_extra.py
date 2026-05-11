"""
Testes de integração adicionais — Tarefa 2.1
Testam os endpoints HTTP com o cliente de testes do Flask (routes + services + models).
"""

import pytest

from app import create_app, services


@pytest.fixture
def client():
    app = create_app(testing=True)
    services.reset_store()
    return app.test_client()


class TestBooksEndpointsIntegration:
    def test_create_book_returns_201_with_id(self, client):
        resp = client.post("/books", json={"title": "Duna", "author": "Herbert"})
        assert resp.status_code == 201
        data = resp.get_json()
        assert "id" in data
        assert data["title"] == "Duna"

    def test_list_books_empty_returns_empty_array(self, client):
        resp = client.get("/books")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_list_books_after_create_returns_one_item(self, client):
        client.post("/books", json={"title": "Livro", "author": "Autor"})
        resp = client.get("/books")
        assert resp.status_code == 200
        assert len(resp.get_json()) == 1

    def test_get_single_book_by_id(self, client):
        created = client.post(
            "/books", json={"title": "Clean Code", "author": "Martin"}
        ).get_json()
        resp = client.get(f"/books/{created['id']}")
        assert resp.status_code == 200
        assert resp.get_json()["title"] == "Clean Code"

    def test_get_nonexistent_book_returns_404(self, client):
        resp = client.get("/books/9999")
        assert resp.status_code == 404

    def test_update_book_changes_title(self, client):
        created = client.post(
            "/books", json={"title": "Antigo", "author": "Autor"}
        ).get_json()
        resp = client.put(
            f"/books/{created['id']}", json={"title": "Novo"}
        )
        assert resp.status_code == 200
        assert resp.get_json()["title"] == "Novo"

    def test_delete_book_returns_success_then_404(self, client):
        created = client.post(
            "/books", json={"title": "Livro", "author": "Autor"}
        ).get_json()
        del_resp = client.delete(f"/books/{created['id']}")
        assert del_resp.status_code == 200
        get_resp = client.get(f"/books/{created['id']}")
        assert get_resp.status_code == 404

    def test_borrow_book_endpoint_sets_unavailable(self, client):
        created = client.post(
            "/books", json={"title": "B", "author": "A"}
        ).get_json()
        resp = client.post(f"/books/{created['id']}/borrow")
        assert resp.status_code == 200
        assert resp.get_json()["available"] is False

    def test_return_book_endpoint_sets_available(self, client):
        created = client.post(
            "/books", json={"title": "B", "author": "A"}
        ).get_json()
        client.post(f"/books/{created['id']}/borrow")
        resp = client.post(f"/books/{created['id']}/return")
        assert resp.status_code == 200
        assert resp.get_json()["available"] is True

    def test_borrow_nonexistent_book_returns_404(self, client):
        resp = client.post("/books/9999/borrow")
        assert resp.status_code == 404

    def test_return_nonexistent_book_returns_404(self, client):
        resp = client.post("/books/9999/return")
        assert resp.status_code == 404

    def test_create_book_missing_title_returns_400(self, client):
        resp = client.post("/books", json={"author": "Autor"})
        assert resp.status_code == 400
        assert "errors" in resp.get_json()

    def test_stats_endpoint_returns_correct_counts(self, client):
        client.post("/books", json={"title": "B1", "author": "A1", "year": 2000})
        client.post("/books", json={"title": "B2", "author": "A2", "year": 2020})
        resp = client.get("/books/stats")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total"] == 2
        assert data["available"] == 2
        assert data["average_year"] == 2010.0

    def test_search_endpoint_filters_by_query(self, client):
        client.post("/books", json={"title": "Python Guide", "author": "Autor"})
        client.post("/books", json={"title": "Java Basics", "author": "Autor"})
        resp = client.get("/books?q=python")
        results = resp.get_json()
        assert len(results) == 1
        assert results[0]["title"] == "Python Guide"
