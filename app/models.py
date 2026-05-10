class Book:
    def __init__(self, id, title, author, year=0, genre="", available=True):
        self.id = id
        self.title = title
        self.author = author
        self.year = year
        self.genre = genre
        self.available = available

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "genre": self.genre,
            "available": self.available,
        }

    @staticmethod
    def validate(data):
        errors = []
        if not data.get("title", "").strip():
            errors.append("Title is required")
        if not data.get("author", "").strip():
            errors.append("Author is required")
        if "year" in data and data["year"] is not None:
            try:
                year = int(data["year"])
                if year < 0 or year > 2100:
                    errors.append("Year must be between 0 and 2100")
            except (ValueError, TypeError):
                errors.append("Year must be a number")
        return errors
