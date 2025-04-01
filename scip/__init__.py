import os

from flask import Flask
from flask_cors import CORS

from scip.routes import add_routes


def get_app():
    app = Flask(__name__)
    CORS(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DB", "postgresql://scip_ro@db.pcic.uvic.ca/scip"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

    add_routes(app)
    return app
