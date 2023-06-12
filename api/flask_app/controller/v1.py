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

REQUEST = {"cmd": None, "args": None}
REQUEST_TIMEOUT = 2500
REQUEST_RETRIES = 3


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def send_request(req: dict):
    """
    This method is for sending request for the backend-service
    it capsulates lot of the logic required to make a successful
    request. The method always returns a reply even when the server doesn't
    respond.
    """
    __context = zmq.Context.instance()
    _client: zmq.Socket = __context.socket(zmq.REQ)
    _client.connect(os.environ.get("SOCKET_ADDRESS", "tcp://0.0.0.0:5555"))

    _poll = zmq.Poller()
    _poll.register(_client, zmq.POLLIN)

    sequence = 0
    retries_left = REQUEST_RETRIES
    while retries_left:
        sequence += 1

        print("Sending request to server")
        _client.send_json(req)

        expect_reply = True
        while expect_reply:
            socks = dict(_poll.poll(REQUEST_TIMEOUT))
            if socks.get(_client) == zmq.POLLIN:
                reply = _client.recv_json()
                # No reply -> Try again.
                if not reply:
                    break
                # Reply received so stop.
                else:
                    print("Response from server", reply)
                    retries_left = REQUEST_RETRIES
                    expect_reply = False
            else:
                print("No response from server, retrying…")
                _client.setsockopt(zmq.LINGER, 0)
                _client.close()
                _poll.unregister(_client)
                retries_left -= 1
                if retries_left == 0:
                    print("Server seems to be offline, abandoning")
                    break
                print("Reconnecting and resending request")
                # Create new connection
                _client: zmq.Socket = __context.socket(zmq.REQ)
                _client.connect(os.environ.get("SOCKET_ADDRESS", "tcp://0.0.0.0:5555"))
                _poll.register(_client, zmq.POLLIN)
                _client.send_json(req)

            return reply


@bp.route("/version", methods=["GET"])
def index():
    return jsonify({"version": "1.0"}), 200


@bp.route("/tasks", methods=["GET"])
def get_tasks():
    req = REQUEST.copy()
    req["cmd"] = "GET-TASKS"
    reply = send_request(req)

    return jsonify({"tasks": reply["tasks"]}), 200


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

    file = request.files["file"]

    if "cmd" not in request.form:
        return jsonify({"status": "command to run is not specified"}), 400

    command = request.form["cmd"]

    if "rt" not in request.form:
        return jsonify({"status": "return type is not specified"}), 400

    return_type = request.form["rt"]

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

        req = REQUEST.copy()
        req["cmd"] = "CREATE-TASK"
        req["args"] = [task_name, command, return_type]
        send_request(req)

        return jsonify({"status": f"task: {task_name} created successfuly."}), 201

    else:
        return jsonify({"status": "Error!"}), 500


@bp.route("/tasks/<string:task_name>", methods=["DELETE"])
def delete_task(task_name: str):
    # 1. check the task exists
    # 2. shutdown the task if it is running
    # 3. delete the task
    # 4. delete the task folder
    if task_name not in os.listdir(current_app.config["UPLOAD_DIRECTORY"]):
        return jsonify({"status": "task does not exist"}), 204

    req = REQUEST.copy()
    req["cmd"] = "DELETE-TASK"
    req["args"] = [task_name]
    reply = send_request(req)

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

    req = REQUEST.copy()
    req["cmd"] = "START-TASK"
    req["args"] = [task_name]
    reply = send_request(req)

    return jsonify(reply), 200


@bp.route("/tasks/<string:task_name>/stop", methods=["POST"])
def stop_task(task_name: str):
    # 1. check the task exists
    # 2. stop the task if it is running
    if task_name not in os.listdir(current_app.config["UPLOAD_DIRECTORY"]):
        return jsonify({"status": "task does not exist"}), 404

    req = REQUEST.copy()
    req["cmd"] = "STOP-TASK"
    req["args"] = [task_name]
    reply = send_request(req)

    return jsonify(reply), 200 if reply["status"] == "ok" else 404


@bp.route("/tasks/<string:task_name>/status", methods=["GET"])
def task_status(task_name: str):
    # TODO:
    # 1. check the task exists
    # 2. get the task status
    if task_name not in os.listdir(current_app.config["UPLOAD_DIRECTORY"]):
        return jsonify({"status": "task does not exist"}), 404

    req = REQUEST.copy()
    req["cmd"] = "TASK-STATUS"
    req["args"] = [task_name]
    reply = send_request(req)

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
