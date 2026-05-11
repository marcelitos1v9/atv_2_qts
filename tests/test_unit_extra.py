"""
Testes unitários adicionais — Tarefa 2.1
Cobrem casos de borda e cenários não presentes nos testes originais de aula.
"""

import pytest

from app import services
from app.models import Book


@pytest.fixture(autouse=True)
def reset():
    services.reset_store()


class TestBookModelExtra:
    def test_book_validate_year_2100_valid(self):
        errors = Book.validate({"title": "T", "author": "A", "year": 2100})
        assert errors == []

    def test_book_validate_year_zero_valid(self):
        errors = Book.validate({"title": "T", "author": "A", "year": 0})
        assert errors == []

    def test_book_validate_year_2101_invalid(self):
        errors = Book.validate({"title": "T", "author": "A", "year": 2101})
        assert "Year must be between 0 and 2100" in errors

    def test_book_to_dict_includes_genre(self):
        book = Book(1, "Title", "Author", 2020, "Science Fiction")
        assert book.to_dict()["genre"] == "Science Fiction"

    def test_book_to_dict_genre_default_empty_string(self):
        book = Book(1, "Title", "Author")
        assert book.to_dict()["genre"] == ""

    def test_book_validate_year_as_string_number(self):
        errors = Book.validate({"title": "T", "author": "A", "year": "2020"})
        assert errors == []

    def test_book_validate_both_fields_missing(self):
        errors = Book.validate({})
        assert "Title is required" in errors
        assert "Author is required" in errors


class TestBookServicesExtra:
    def test_create_book_with_genre_stores_correctly(self):
        book, _ = services.create_book(
            {"title": "Duna", "author": "Herbert", "genre": "Sci-Fi"}
        )
        assert book.genre == "Sci-Fi"

    def test_create_book_strips_title_whitespace(self):
        book, _ = services.create_book({"title": "  Título  ", "author": "Autor"})
        assert book.title == "Título"

    def test_create_book_strips_author_whitespace(self):
        book, _ = services.create_book({"title": "Título", "author": "  Autor  "})
        assert book.author == "Autor"

    def test_get_stats_unavailable_count(self):
        b, _ = services.create_book({"title": "B1", "author": "A1"})
        services.create_book({"title": "B2", "author": "A2"})
        services.borrow_book(b.id)
        stats = services.get_stats()
        assert stats["unavailable"] == 1
        assert stats["available"] == 1

    def test_get_stats_skips_zero_year_in_average(self):
        services.create_book({"title": "SemAno", "author": "A"})
        services.create_book({"title": "ComAno", "author": "B", "year": 2000})
        stats = services.get_stats()
        assert stats["average_year"] == 2000.0

    def test_update_book_available_field(self):
        book, _ = services.create_book({"title": "B", "author": "A"})
        updated, errors = services.update_book(book.id, {"available": False})
        assert errors == []
        assert updated.available is False

    def test_update_book_preserves_unchanged_fields(self):
        book, _ = services.create_book(
            {"title": "Orig", "author": "Autor", "year": 2000, "genre": "Drama"}
        )
        updated, _ = services.update_book(book.id, {"title": "Novo"})
        assert updated.author == "Autor"
        assert updated.year == 2000
        assert updated.genre == "Drama"

    def test_search_returns_multiple_matches(self):
        services.create_book({"title": "Python Básico", "author": "Ana"})
        services.create_book({"title": "Python Avançado", "author": "Bob"})
        services.create_book({"title": "Java", "author": "Carlos"})
        results = services.search_books("python")
        assert len(results) == 2

    def test_borrow_sets_unavailable_then_return_sets_available(self):
        book, _ = services.create_book({"title": "B", "author": "A"})
        services.borrow_book(book.id)
        assert services.get_book(book.id).available is False
        services.return_book(book.id)
        assert services.get_book(book.id).available is True

    def test_get_stats_average_year_rounded_one_decimal(self):
        services.create_book({"title": "B1", "author": "A", "year": 2001})
        services.create_book({"title": "B2", "author": "A", "year": 2002})
        services.create_book({"title": "B3", "author": "A", "year": 2003})
        stats = services.get_stats()
        assert stats["average_year"] == 2002.0
