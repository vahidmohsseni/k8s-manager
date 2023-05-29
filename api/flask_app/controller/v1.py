from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
import os
import zmq

ALLOWED_EXTENSIONS = set(
    [
        "py",
    ]
)

bp = Blueprint("v1", __name__, url_prefix="/api/v1")

__context = zmq.Context.instance()
_request: zmq.Socket = __context.socket(zmq.REQ)
_request.connect("tcp://localhost:5555")

REQUEST = {"cmd": None, "args": None}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/version", methods=["GET"])
def index():
    return jsonify({"version": "1.0"}), 200


@bp.route("/tasks", methods=["GET"])
def get_tasks():
    cmd = REQUEST.copy()
    cmd["cmd"] = "GET-TASKS"
    _request.send_json(cmd)
    reply = _request.recv_json()
    if isinstance(reply, dict):
        print("from server", reply)
    if len(reply["tasks"]) > 0:
        return jsonify({"tasks": reply["tasks"]}), 200
    return jsonify({"tasks": reply["tasks"]}), 404


@bp.route("/tasks/<string:task_name>", methods=["POST"])
def create_task(task_name: str):
    """
    1. check if the task_name does not exist
    2. create the task folder
    3. TODO: send the task to backend service to be scheduled
    """
    # TODO: add example when returning error
    if "file" not in request.files:
        return jsonify({"status": "file required in the request"}), 400

    if "cmd" not in request.form:
        return jsonify({"status": "command to run is not specified"}), 400

    command = request.form["cmd"]

    if "rt" not in request.form:
        return jsonify({"status": "return type is not specified"}), 400

    return_type = request.form["rt"]

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"status": "no file"}), 400

    if task_name in os.listdir(current_app.config["UPLOAD_DIRECTORY"]):
        return jsonify({"status": "task already exists"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        os.makedirs(os.path.join(current_app.config["UPLOAD_DIRECTORY"], task_name))
        file.save(
            os.path.join(current_app.config["UPLOAD_DIRECTORY"], task_name, filename)
        )
        cmd = REQUEST.copy()
        cmd["cmd"] = "CREATE-TASK"
        cmd["args"] = [task_name, command, return_type]
        _request.send_json(cmd)
        return jsonify({"status": f"task: {task_name} created successfuly."}), 201

    return jsonify({"status": "Error!"}), 400


@bp.route("/tasks/<string:task_name>", methods=["DELETE"])
def delete_task(task_name: str):
    # 1. check the task exists
    # 2. shutdown the task if it is running
    # 3. delete the task
    # 4. delete the task folder
    if task_name not in os.listdir(current_app.config["UPLOAD_DIRECTORY"]):
        return jsonify({"status": "task does not exist"}), 404

    cmd = REQUEST.copy()
    cmd["cmd"] = "DELETE-TASK"
    cmd["args"] = [task_name]
    _request.send_json(cmd)
    reply = _request.recv_json()
    print("from server", reply)
    os.remove(
        os.path.join(
            current_app.config["UPLOAD_DIRECTORY"],
            task_name,
            os.listdir(os.path.join(current_app.config["UPLOAD_DIRECTORY"], task_name))[
                0
            ],
        )
    )
    os.rmdir(os.path.join(current_app.config["UPLOAD_DIRECTORY"], task_name))
    return (
        jsonify(
            {
                "status": f"task: {task_name} deleted successfuly from API host.",
                "backend-status": reply,
            }
        ),
        200,
    )


@bp.route("/tasks/<string:task_name>", methods=["PUT"])
def update_task(task_name: str):
    # TODO:
    # 1. check the task exists
    # 2. shutdown the task if it is running
    # 3. update the task
    return jsonify({"task": task_name}), 200


@bp.route("/tasks/<string:task_name>/start", methods=["POST"])
def start_task(task_name: str):
    # 1. check the task exists
    # 2. start the task if it is not running
    if task_name not in os.listdir(current_app.config["UPLOAD_DIRECTORY"]):
        return jsonify({"status": "task does not exist"}), 404

    cmd = REQUEST.copy()
    cmd["cmd"] = "START-TASK"
    cmd["args"] = [task_name]
    _request.send_json(cmd)
    reply = _request.recv_json()
    return jsonify(reply), 200


@bp.route("/tasks/<string:task_name>/stop", methods=["POST"])
def stop_task(task_name: str):
    # 1. check the task exists
    # 2. stop the task if it is running
    if task_name not in os.listdir(current_app.config["UPLOAD_DIRECTORY"]):
        return jsonify({"status": "task does not exist"}), 404

    cmd = REQUEST.copy()
    cmd["cmd"] = "STOP-TASK"
    cmd["args"] = [task_name]
    _request.send_json(cmd)
    reply = _request.recv_json()
    return jsonify(reply), 200 if reply["status"] == "ok" else 404


@bp.route("/tasks/<string:task_name>/status", methods=["GET"])
def task_status(task_name: str):
    # TODO:
    # 1. check the task exists
    # 2. get the task status
    if task_name not in os.listdir(current_app.config["UPLOAD_DIRECTORY"]):
        return jsonify({"status": "task does not exist"}), 404

    cmd = REQUEST.copy()
    cmd["cmd"] = "TASK-STATUS"
    cmd["args"] = [task_name]
    _request.send_json(cmd)
    reply = _request.recv_json()
    return jsonify(reply), 200


@bp.route("/tasks/<string:task_name>/results", methods=["GET"])
def task_results(task_name: str):
    # TODO:
    # 1. check the task exists
    # 2. get the task results
    return jsonify({"task": task_name}), 200


@bp.route("/tasks/<string:task_name>/download", methods=["GET"])
def download_task(task_name: str):
    uploads = os.path.join(current_app.config["UPLOAD_DIRECTORY"], task_name)
    if len(os.listdir(uploads)) == 0:
        return jsonify({"status": "task does not exist"}), 404

    return send_from_directory(uploads, os.listdir(uploads)[0])
