class TestListBooks:
    def test_list_books_empty(self, client):
        response = client.get("/books")
        assert response.status_code == 200
        assert response.get_json() == []

    def test_list_books_returns_all(self, client):
        client.post("/books", json={"title": "B1", "author": "A1"})
        client.post("/books", json={"title": "B2", "author": "A2"})
        response = client.get("/books")
        assert response.status_code == 200
        assert len(response.get_json()) == 2


class TestCreateBook:
    def test_create_book_success(self, client):
        response = client.post(
            "/books",
            json={"title": "Clean Code", "author": "Robert Martin", "year": 2008},
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["title"] == "Clean Code"
        assert data["id"] is not None
        assert data["available"] is True

    def test_create_book_missing_title(self, client):
        response = client.post("/books", json={"author": "Author"})
        assert response.status_code == 400
        assert "errors" in response.get_json()

    def test_create_book_missing_author(self, client):
        response = client.post("/books", json={"title": "Title"})
        assert response.status_code == 400

    def test_create_book_empty_body(self, client):
        response = client.post("/books", json={})
        assert response.status_code == 400

    def test_create_book_no_json(self, client):
        response = client.post("/books", data="not json")
        assert response.status_code in (400, 415)

    def test_create_book_with_genre(self, client):
        response = client.post(
            "/books",
            json={"title": "Dune", "author": "Herbert", "genre": "Sci-Fi"},
        )
        assert response.status_code == 201
        assert response.get_json()["genre"] == "Sci-Fi"

    def test_create_book_invalid_year(self, client):
        response = client.post(
            "/books",
            json={"title": "T", "author": "A", "year": "invalid"},
        )
        assert response.status_code == 400


class TestGetBook:
    def test_get_book_success(self, client, sample_book):
        book_id = sample_book["id"]
        response = client.get(f"/books/{book_id}")
        assert response.status_code == 200
        assert response.get_json()["title"] == "Clean Code"

    def test_get_nonexistent_book_returns_404(self, client):
        response = client.get("/books/999")
        assert response.status_code == 404
        assert "error" in response.get_json()


class TestUpdateBook:
    def test_update_book_title(self, client, sample_book):
        book_id = sample_book["id"]
        response = client.put(f"/books/{book_id}", json={"title": "Updated"})
        assert response.status_code == 200
        assert response.get_json()["title"] == "Updated"

    def test_update_book_partial(self, client, sample_book):
        book_id = sample_book["id"]
        response = client.put(f"/books/{book_id}", json={"year": 2024})
        assert response.status_code == 200
        data = response.get_json()
        assert data["year"] == 2024
        assert data["title"] == "Clean Code"

    def test_update_nonexistent_book_returns_404(self, client):
        response = client.put("/books/999", json={"title": "New"})
        assert response.status_code == 404

    def test_update_book_no_body(self, client, sample_book):
        book_id = sample_book["id"]
        response = client.put(f"/books/{book_id}", data="not json")
        assert response.status_code in (400, 415)


class TestDeleteBook:
    def test_delete_book_success(self, client, sample_book):
        book_id = sample_book["id"]
        response = client.delete(f"/books/{book_id}")
        assert response.status_code == 200
        assert client.get(f"/books/{book_id}").status_code == 404

    def test_delete_nonexistent_book_returns_404(self, client):
        response = client.delete("/books/999")
        assert response.status_code == 404


class TestSearchBooks:
    def test_search_by_title(self, client):
        client.post("/books", json={"title": "Python Tricks", "author": "Dan Bader"})
        client.post("/books", json={"title": "Effective Java", "author": "Bloch"})
        response = client.get("/books?q=python")
        assert response.status_code == 200
        results = response.get_json()
        assert len(results) == 1
        assert results[0]["title"] == "Python Tricks"

    def test_search_no_results(self, client):
        client.post("/books", json={"title": "Java", "author": "Author"})
        response = client.get("/books?q=python")
        assert response.get_json() == []

    def test_search_empty_query_returns_all(self, client):
        client.post("/books", json={"title": "B1", "author": "A1"})
        client.post("/books", json={"title": "B2", "author": "A2"})
        response = client.get("/books?q=")
        assert len(response.get_json()) == 2


class TestStats:
    def test_get_stats_empty(self, client):
        response = client.get("/books/stats")
        assert response.status_code == 200
        data = response.get_json()
        assert data["total"] == 0

    def test_get_stats_with_books(self, client, sample_book):
        response = client.get("/books/stats")
        data = response.get_json()
        assert data["total"] >= 1
        assert "available" in data
        assert "unavailable" in data


class TestBorrowReturn:
    def test_borrow_book(self, client, sample_book):
        book_id = sample_book["id"]
        response = client.post(f"/books/{book_id}/borrow")
        assert response.status_code == 200
        assert response.get_json()["available"] is False

    def test_borrow_unavailable_book_returns_409(self, client, sample_book):
        book_id = sample_book["id"]
        client.post(f"/books/{book_id}/borrow")
        response = client.post(f"/books/{book_id}/borrow")
        assert response.status_code == 409

    def test_borrow_nonexistent_book_returns_404(self, client):
        response = client.post("/books/999/borrow")
        assert response.status_code == 404

    def test_return_book(self, client, sample_book):
        book_id = sample_book["id"]
        client.post(f"/books/{book_id}/borrow")
        response = client.post(f"/books/{book_id}/return")
        assert response.status_code == 200
        assert response.get_json()["available"] is True

    def test_return_available_book_returns_409(self, client, sample_book):
        book_id = sample_book["id"]
        response = client.post(f"/books/{book_id}/return")
        assert response.status_code == 409

    def test_return_nonexistent_book_returns_404(self, client):
        response = client.post("/books/999/return")
        assert response.status_code == 404
