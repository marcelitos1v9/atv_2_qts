from flask import Flask


def create_app(testing=False):
    app = Flask(__name__)

    if testing:
        app.config["TESTING"] = True

    from app.routes import books_bp

    app.register_blueprint(books_bp)

    return app
