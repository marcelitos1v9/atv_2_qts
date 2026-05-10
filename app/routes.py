from flask import Blueprint, jsonify, render_template, request

from app import services

books_bp = Blueprint("books", __name__)


@books_bp.route("/")
def index():
    return render_template("index.html")


@books_bp.route("/books/stats", methods=["GET"])
def stats():
    return jsonify(services.get_stats())


@books_bp.route("/books", methods=["GET"])
def list_books():
    query = request.args.get("q", "")
    books = services.search_books(query)
    return jsonify([b.to_dict() for b in books])


@books_bp.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = services.get_book(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book.to_dict())


@books_bp.route("/books", methods=["POST"])
def create_book():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    book, errors = services.create_book(data)
    if errors:
        return jsonify({"errors": errors}), 400
    return jsonify(book.to_dict()), 201


@books_bp.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    book, errors = services.update_book(book_id, data)
    if errors:
        return jsonify({"errors": errors}), 404
    return jsonify(book.to_dict())


@books_bp.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    deleted = services.delete_book(book_id)
    if not deleted:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"message": "Book deleted successfully"})


@books_bp.route("/books/<int:book_id>/borrow", methods=["POST"])
def borrow_book(book_id):
    book, error = services.borrow_book(book_id)
    if error:
        status = 404 if "not found" in error else 409
        return jsonify({"error": error}), status
    return jsonify(book.to_dict())


@books_bp.route("/books/<int:book_id>/return", methods=["POST"])
def return_book(book_id):
    book, error = services.return_book(book_id)
    if error:
        status = 404 if "not found" in error else 409
        return jsonify({"error": error}), status
    return jsonify(book.to_dict())
