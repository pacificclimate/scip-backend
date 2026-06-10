from flask import jsonify, request
from sqlalchemy import text

import scip.api as api


def add_routes(app, db):
    @app.route("/api/readyz")
    def readyz():
        status = {"status": "ok"}
        http_status = 200

        if request.args.get("verbose", "").lower() in {"1", "true", "yes"}:
            try:
                db.session.execute(text("SELECT 1"))
                status["db"] = "ok"
            except Exception as exc:
                status["status"] = "error"
                status["db"] = str(exc)
                http_status = 503

        response = jsonify(status)
        response.cache_control.no_store = True
        return response, http_status

    @app.route("/api/<request_type>", methods=["GET", "POST"])
    def api_request(*args, **kwargs):
        return api.call(db.session, *args, **kwargs)

    @app.after_request
    def add_header(response):
        if request.endpoint != "readyz":
            response.cache_control.public = True
            response.cache_control.max_age = 86400
        return response
