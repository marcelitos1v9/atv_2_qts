"""
Testes funcionais adicionais — Tarefa 2.1
Testam fluxos completos de usuário: sequências de operações que representam
casos de uso reais da aplicação de biblioteca.
"""

import pytest

from app import create_app, services


@pytest.fixture
def client():
    app = create_app(testing=True)
    services.reset_store()
    return app.test_client()


def test_full_book_lifecycle(client):
    """Fluxo completo: criar → atualizar → emprestar → devolver → excluir."""
    created = client.post(
        "/books", json={"title": "Orig", "author": "Autor", "year": 2000}
    ).get_json()
    book_id = created["id"]

    updated = client.put(f"/books/{book_id}", json={"title": "Atualizado"}).get_json()
    assert updated["title"] == "Atualizado"

    borrowed = client.post(f"/books/{book_id}/borrow").get_json()
    assert borrowed["available"] is False

    returned = client.post(f"/books/{book_id}/return").get_json()
    assert returned["available"] is True

    del_resp = client.delete(f"/books/{book_id}")
    assert del_resp.status_code == 200

    assert client.get(f"/books/{book_id}").status_code == 404


def test_search_workflow_filters_correctly(client):
    """Criar vários livros e verificar que a busca retorna apenas os relevantes."""
    client.post("/books", json={"title": "Refactoring", "author": "Fowler"})
    client.post("/books", json={"title": "Clean Code", "author": "Martin"})
    client.post("/books", json={"title": "Design Patterns", "author": "Gang of Four"})

    resp = client.get("/books?q=fowler")
    results = resp.get_json()
    assert len(results) == 1
    assert results[0]["title"] == "Refactoring"

    resp_all = client.get("/books")
    assert len(resp_all.get_json()) == 3


def test_stats_reflect_borrow_state(client):
    """Verificar que as estatísticas refletem corretamente os livros emprestados."""
    b1 = client.post(
        "/books", json={"title": "B1", "author": "A", "year": 2010}
    ).get_json()
    b2 = client.post(
        "/books", json={"title": "B2", "author": "A", "year": 2020}
    ).get_json()
    client.post("/books", json={"title": "B3", "author": "A", "year": 2030})

    client.post(f"/books/{b1['id']}/borrow")
    client.post(f"/books/{b2['id']}/borrow")

    stats = client.get("/books/stats").get_json()
    assert stats["total"] == 3
    assert stats["available"] == 1
    assert stats["unavailable"] == 2
    assert stats["average_year"] == 2020.0


def test_double_borrow_returns_conflict(client):
    """Tentar emprestar um livro já emprestado deve retornar erro 409."""
    created = client.post("/books", json={"title": "B", "author": "A"}).get_json()
    book_id = created["id"]

    first = client.post(f"/books/{book_id}/borrow")
    assert first.status_code == 200

    second = client.post(f"/books/{book_id}/borrow")
    assert second.status_code == 409


def test_return_book_not_borrowed_returns_conflict(client):
    """Devolver livro que não está emprestado deve retornar erro 409."""
    created = client.post("/books", json={"title": "B", "author": "A"}).get_json()
    resp = client.post(f"/books/{created['id']}/return")
    assert resp.status_code == 409


def test_create_multiple_books_and_delete_one(client):
    """Criar vários livros, excluir um e garantir que os outros persistem."""
    b1 = client.post("/books", json={"title": "B1", "author": "A"}).get_json()
    client.post("/books", json={"title": "B2", "author": "A"})
    client.post("/books", json={"title": "B3", "author": "A"})

    client.delete(f"/books/{b1['id']}")

    all_books = client.get("/books").get_json()
    assert len(all_books) == 2
    ids = [b["id"] for b in all_books]
    assert b1["id"] not in ids
