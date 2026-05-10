import pytest

from app import services
from app.models import Book


@pytest.fixture(autouse=True)
def reset():
    services.reset_store()


# ── Testes do modelo Book ────────────────────────────────────────────────────


class TestBookModel:
    def test_book_creation(self):
        book = Book(1, "Test Book", "Test Author", 2020)
        assert book.id == 1
        assert book.title == "Test Book"
        assert book.author == "Test Author"
        assert book.year == 2020

    def test_book_default_available(self):
        book = Book(1, "Test", "Author")
        assert book.available is True

    def test_book_default_genre(self):
        book = Book(1, "Test", "Author")
        assert book.genre == ""

    def test_book_to_dict(self):
        book = Book(1, "Test Book", "Test Author", 2020, "Fiction", True)
        assert book.to_dict() == {
            "id": 1,
            "title": "Test Book",
            "author": "Test Author",
            "year": 2020,
            "genre": "Fiction",
            "available": True,
        }

    def test_book_available_false(self):
        book = Book(2, "Title", "Author", available=False)
        assert book.available is False
        assert book.to_dict()["available"] is False

    def test_book_validate_empty_title(self):
        errors = Book.validate({"title": "", "author": "Author"})
        assert "Title is required" in errors

    def test_book_validate_whitespace_title(self):
        errors = Book.validate({"title": "   ", "author": "Author"})
        assert "Title is required" in errors

    def test_book_validate_missing_title(self):
        errors = Book.validate({"author": "Author"})
        assert "Title is required" in errors

    def test_book_validate_empty_author(self):
        errors = Book.validate({"title": "Title", "author": ""})
        assert "Author is required" in errors

    def test_book_validate_missing_author(self):
        errors = Book.validate({"title": "Title"})
        assert "Author is required" in errors

    def test_book_validate_invalid_year_string(self):
        errors = Book.validate({"title": "T", "author": "A", "year": "abc"})
        assert "Year must be a number" in errors

    def test_book_validate_year_too_large(self):
        errors = Book.validate({"title": "T", "author": "A", "year": 9999})
        assert "Year must be between 0 and 2100" in errors

    def test_book_validate_negative_year(self):
        errors = Book.validate({"title": "T", "author": "A", "year": -1})
        assert "Year must be between 0 and 2100" in errors

    def test_book_validate_valid_data(self):
        errors = Book.validate({"title": "Test", "author": "Author", "year": 2020})
        assert errors == []

    def test_book_validate_no_year(self):
        errors = Book.validate({"title": "Test", "author": "Author"})
        assert errors == []


# ── Testes da camada de serviço ──────────────────────────────────────────────


class TestBookServices:
    def test_create_book_returns_book(self):
        book, errors = services.create_book({"title": "Test", "author": "Author"})
        assert book is not None
        assert errors == []

    def test_create_book_assigns_id(self):
        book, _ = services.create_book({"title": "T1", "author": "A1"})
        assert book.id == 1

    def test_create_book_increments_id(self):
        b1, _ = services.create_book({"title": "T1", "author": "A1"})
        b2, _ = services.create_book({"title": "T2", "author": "A2"})
        assert b1.id != b2.id

    def test_create_book_invalid_returns_errors(self):
        book, errors = services.create_book({"title": "", "author": ""})
        assert book is None
        assert len(errors) > 0

    def test_get_book_returns_correct_book(self):
        book, _ = services.create_book({"title": "Found", "author": "Author"})
        result = services.get_book(book.id)
        assert result is not None
        assert result.title == "Found"

    def test_get_nonexistent_book_returns_none(self):
        assert services.get_book(999) is None

    def test_get_all_books_empty(self):
        assert services.get_all_books() == []

    def test_get_all_books_returns_all(self):
        services.create_book({"title": "B1", "author": "A1"})
        services.create_book({"title": "B2", "author": "A2"})
        assert len(services.get_all_books()) == 2

    def test_update_book(self):
        book, _ = services.create_book({"title": "Old", "author": "Author"})
        updated, errors = services.update_book(book.id, {"title": "New"})
        assert errors == []
        assert updated.title == "New"

    def test_update_nonexistent_book_returns_error(self):
        book, errors = services.update_book(999, {"title": "New"})
        assert book is None
        assert "Book not found" in errors

    def test_delete_book(self):
        book, _ = services.create_book({"title": "ToDelete", "author": "Author"})
        result = services.delete_book(book.id)
        assert result is True
        assert services.get_book(book.id) is None

    def test_delete_nonexistent_book_returns_false(self):
        assert services.delete_book(999) is False

    def test_search_books_by_title(self):
        services.create_book({"title": "Python Programming", "author": "Guido"})
        results = services.search_books("python")
        assert len(results) == 1

    def test_search_books_case_insensitive(self):
        services.create_book({"title": "PYTHON", "author": "Author"})
        assert len(services.search_books("python")) == 1
        assert len(services.search_books("PYTHON")) == 1

    def test_search_by_author(self):
        services.create_book({"title": "Book", "author": "Martin Fowler"})
        results = services.search_books("fowler")
        assert len(results) == 1

    def test_search_no_match_returns_empty(self):
        services.create_book({"title": "Java", "author": "Someone"})
        assert services.search_books("python") == []

    def test_search_empty_query_returns_all(self):
        services.create_book({"title": "B1", "author": "A1"})
        services.create_book({"title": "B2", "author": "A2"})
        assert len(services.search_books("")) == 2

    def test_get_stats_empty_store(self):
        stats = services.get_stats()
        assert stats["total"] == 0
        assert stats["available"] == 0
        assert stats["average_year"] is None

    def test_get_stats_counts(self):
        services.create_book({"title": "B1", "author": "A1", "year": 2000})
        services.create_book({"title": "B2", "author": "A2", "year": 2020})
        stats = services.get_stats()
        assert stats["total"] == 2
        assert stats["available"] == 2
        assert stats["average_year"] == 2010.0

    def test_borrow_book_sets_unavailable(self):
        book, _ = services.create_book({"title": "B", "author": "A"})
        updated, error = services.borrow_book(book.id)
        assert error is None
        assert updated.available is False

    def test_borrow_nonexistent_book(self):
        book, error = services.borrow_book(999)
        assert book is None
        assert "not found" in error

    def test_borrow_unavailable_book_returns_error(self):
        book, _ = services.create_book({"title": "B", "author": "A"})
        services.borrow_book(book.id)
        _, error = services.borrow_book(book.id)
        assert error is not None

    def test_return_book_sets_available(self):
        book, _ = services.create_book({"title": "B", "author": "A"})
        services.borrow_book(book.id)
        updated, error = services.return_book(book.id)
        assert error is None
        assert updated.available is True

    def test_return_nonexistent_book(self):
        book, error = services.return_book(999)
        assert book is None
        assert "not found" in error

    def test_return_available_book_returns_error(self):
        book, _ = services.create_book({"title": "B", "author": "A"})
        _, error = services.return_book(book.id)
        assert error is not None
