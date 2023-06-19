from flask import Blueprint, Response, send_from_directory
from utils import file_exists, get_filenames, UPLOAD_DIR

routes = Blueprint("routes", __name__)


@routes.get("/")
def get_index():
    """Health check endpoint"""
    return Response(status=200)


@routes.get("/models")
def get_all_models():
    """Return list of models"""
    return get_filenames()


@routes.post("/models")
def post_model():
    """Upload a model onto server for training"""
    return "OK"


@routes.get("/models/<string:model_id>")
def get_model(model_id):
    if file_exists(model_id):
        return send_from_directory(UPLOAD_DIR, model_id)
    return Response(status=404)
