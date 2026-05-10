from app.models import Book

_books: dict = {}
_next_id: int = 1


def reset_store():
    global _books, _next_id
    _books = {}
    _next_id = 1


def create_book(data):
    global _next_id
    errors = Book.validate(data)
    if errors:
        return None, errors

    book = Book(
        id=_next_id,
        title=data["title"].strip(),
        author=data["author"].strip(),
        year=int(data["year"]) if data.get("year") else 0,
        genre=data.get("genre", "").strip(),
        available=data.get("available", True),
    )
    _books[_next_id] = book
    _next_id += 1
    return book, []


def get_book(book_id):
    return _books.get(book_id)


def get_all_books():
    return list(_books.values())


def update_book(book_id, data):
    book = _books.get(book_id)
    if not book:
        return None, ["Book not found"]

    if data.get("title"):
        book.title = data["title"].strip()
    if data.get("author"):
        book.author = data["author"].strip()
    if data.get("year") is not None:
        book.year = int(data["year"])
    if "genre" in data:
        book.genre = data["genre"].strip()
    if "available" in data:
        book.available = bool(data["available"])

    return book, []


def delete_book(book_id):
    if book_id not in _books:
        return False
    del _books[book_id]
    return True


def search_books(query):
    if not query:
        return get_all_books()
    q = query.lower()
    return [
        book
        for book in _books.values()
        if q in book.title.lower() or q in book.author.lower()
    ]


def get_stats():
    books = list(_books.values())
    if not books:
        return {
            "total": 0,
            "available": 0,
            "unavailable": 0,
            "average_year": None,
        }

    available_count = sum(1 for b in books if b.available)
    years = [b.year for b in books if b.year and b.year > 0]
    avg_year = sum(years) / len(years) if years else None

    return {
        "total": len(books),
        "available": available_count,
        "unavailable": len(books) - available_count,
        "average_year": round(avg_year, 1) if avg_year is not None else None,
    }


def borrow_book(book_id):
    book = _books.get(book_id)
    if not book:
        return None, "Book not found"
    if not book.available:
        return None, "Book is not available for borrowing"
    book.available = False
    return book, None


def return_book(book_id):
    book = _books.get(book_id)
    if not book:
        return None, "Book not found"
    if book.available:
        return None, "Book was not borrowed"
    book.available = True
    return book, None
