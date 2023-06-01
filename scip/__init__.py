import os

from flask import Flask
from flask_cors import CORS

from scip.routes import add_routes


def get_app():
    print("in get_app")
    app = Flask(__name__)
    CORS(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB")
    app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

    add_routes(app)
    return app
