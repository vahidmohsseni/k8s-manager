import json
from flask import Blueprint, Response, send_from_directory, request, abort
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
from utils import get_model_path, get_filenames, UPLOAD_DIR
from pathlib import Path
from training import enqueue_model, model_in_training
from uuid import uuid4


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
    if "file" not in request.files:
        abort(400, "No file found in upload")
    file = request.files["file"]
    if file.filename == "":
        abort(400, "No file found in upload")
    if file:
        # Keep extension, randomize filename
        if "." not in file.filename:
            abort(400, "File has no extension")
        extension = file.filename.rsplit(".", 1)[1]
        id = secure_filename(str(uuid4().hex))
        file_path = Path(UPLOAD_DIR, id + "." + extension)
        file.save(file_path)
        enqueue_model(id)
        return {"id": id}


@routes.get("/models/<string:model_id>")
def get_model(model_id):
    model = get_model_path(model_id)
    if model:
        return send_from_directory(UPLOAD_DIR, model.name)
    if model_in_training(model_id):
        return Response(status=202, message="Model is being trained, check back later.")
    return Response(status=404)


@routes.errorhandler(HTTPException)
def jsonify_error(e: HTTPException):
    """Handles all error handling from abort functions"""
    response = e.get_response()
    response.data = json.dumps(
        {"code": e.code, "name": e.name, "description": e.description}
    )
    response.content_type = "application/json"
    return response
