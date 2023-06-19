from flask import Blueprint


routes = Blueprint("routes", __name__)


@routes.route("/models")
@routes.get("/")
def get_models():
    """Return list of models"""
    return []


@routes.post("/")
def post_model():
    return "OK"
