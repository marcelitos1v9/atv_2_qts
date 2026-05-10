class TestBookLifecycle:
    def test_complete_crud_lifecycle(self, client):
        create = client.post(
            "/books",
            json={
                "title": "Domain Driven Design",
                "author": "Eric Evans",
                "year": 2003,
            },
        )
        assert create.status_code == 201
        book_id = create.get_json()["id"]

        get = client.get(f"/books/{book_id}")
        assert get.status_code == 200
        assert get.get_json()["title"] == "Domain Driven Design"

        update = client.put(f"/books/{book_id}", json={"year": 2004})
        assert update.status_code == 200
        assert update.get_json()["year"] == 2004

        delete = client.delete(f"/books/{book_id}")
        assert delete.status_code == 200

        assert client.get(f"/books/{book_id}").status_code == 404

    def test_borrow_and_return_flow(self, client):
        book = client.post(
            "/books",
            json={"title": "The Pragmatic Programmer", "author": "Hunt & Thomas"},
        ).get_json()
        book_id = book["id"]

        assert book["available"] is True

        borrow = client.post(f"/books/{book_id}/borrow")
        assert borrow.status_code == 200
        assert borrow.get_json()["available"] is False

        borrow_again = client.post(f"/books/{book_id}/borrow")
        assert borrow_again.status_code == 409

        ret = client.post(f"/books/{book_id}/return")
        assert ret.status_code == 200
        assert ret.get_json()["available"] is True

        ret_again = client.post(f"/books/{book_id}/return")
        assert ret_again.status_code == 409


class TestSearchFlow:
    def test_search_filters_by_title(self, client):
        client.post("/books", json={"title": "Python Cookbook", "author": "Beazley"})
        client.post("/books", json={"title": "Effective Java", "author": "Bloch"})
        client.post(
            "/books",
            json={"title": "Python for Data Science", "author": "VanderPlas"},
        )

        resp = client.get("/books?q=python")
        results = resp.get_json()
        assert len(results) == 2
        titles = [b["title"] for b in results]
        assert "Python Cookbook" in titles
        assert "Python for Data Science" in titles
        assert "Effective Java" not in titles

    def test_search_by_author_name(self, client):
        client.post("/books", json={"title": "Refactoring", "author": "Martin Fowler"})
        client.post(
            "/books",
            json={"title": "Patterns of EAA", "author": "Martin Fowler"},
        )
        client.post("/books", json={"title": "Clean Code", "author": "Bob Martin"})

        resp = client.get("/books?q=fowler")
        results = resp.get_json()
        assert len(results) == 2


class TestStatsFlow:
    def test_stats_reflect_borrow_state(self, client):
        b1 = client.post(
            "/books", json={"title": "B1", "author": "A1", "year": 2000}
        ).get_json()
        client.post("/books", json={"title": "B2", "author": "A2", "year": 2020})
        client.post("/books", json={"title": "B3", "author": "A3", "year": 2010})

        client.post(f"/books/{b1['id']}/borrow")

        stats = client.get("/books/stats").get_json()
        assert stats["total"] == 3
        assert stats["available"] == 2
        assert stats["unavailable"] == 1
        assert stats["average_year"] == 2010.0

    def test_stats_after_delete(self, client):
        b1 = client.post("/books", json={"title": "B1", "author": "A1"}).get_json()
        client.post("/books", json={"title": "B2", "author": "A2"})

        client.delete(f"/books/{b1['id']}")

        stats = client.get("/books/stats").get_json()
        assert stats["total"] == 1
