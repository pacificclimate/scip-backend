import os
from typing import Any

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import NullPool

from scip.routes import add_routes

db = SQLAlchemy()


def _build_engine_options() -> dict[str, Any]:
    """Build SQLAlchemy engine options from environment variables.

    Set SQLALCHEMY_POOL_CLASS=null to use NullPool (recommended when deploying
    behind pgbouncer). Optional pool tuning via SQLALCHEMY_POOL_SIZE,
    SQLALCHEMY_MAX_OVERFLOW, SQLALCHEMY_POOL_TIMEOUT, SQLALCHEMY_POOL_RECYCLE.
    """
    if os.getenv("SQLALCHEMY_POOL_CLASS", "").lower() == "null":
        return {"poolclass": NullPool}

    options: dict[str, Any] = {"pool_pre_ping": True}

    for env_var, key, cast in [
        ("SQLALCHEMY_POOL_SIZE", "pool_size", int),
        ("SQLALCHEMY_MAX_OVERFLOW", "max_overflow", int),
        ("SQLALCHEMY_POOL_TIMEOUT", "pool_timeout", float),
        ("SQLALCHEMY_POOL_RECYCLE", "pool_recycle", float),
    ]:
        value = os.getenv(env_var)
        if value is not None:
            options[key] = cast(value)

    return options


def get_app():
    app = Flask(__name__)
    CORS(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DB", "postgresql://scip_ro@db.pcic.uvic.ca/scip"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Default is already false.
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = _build_engine_options()

    db.init_app(app)

    add_routes(app, db)
    return app
