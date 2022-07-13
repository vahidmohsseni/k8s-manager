from flask import Blueprint, request, jsonify
import zmq
import json

bp = Blueprint("v1", __name__, url_prefix="/api/v1")

__context = zmq.Context.instance()
_request:zmq.Socket = __context.socket(zmq.REQ)
_request.connect("tcp://localhost:5555")

REQUEST = {"cmd": None, "args": None}


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
    ARGS FORMAT: [name, file_address]
    """
    cmd = REQUEST.copy()
    cmd["cmd"] = "CREATE-TASK"
    cmd["args"] = [task_name]
    _request.send()
    return jsonify({"task": task_name}), 201


@bp.route("/tasks/<string:task_name>", methods=["DELETE"])
def delete_task(task_name: str):
    # TODO:
    # 1. check the task exists
    # 2. shutdown the task if it is running
    # 3. delete the task
    return jsonify({"task": task_name}), 200


@bp.route("/tasks/<string:task_name>", methods=["PUT"])
def update_task(task_name: str):
    # TODO:
    # 1. check the task exists
    # 2. shutdown the task if it is running
    # 3. update the task
    return jsonify({"task": task_name}), 200


@bp.route("/tasks/<string:task_name>/start", methods=["POST"])
def start_task(task_name: str):
    # TODO:
    # 1. check the task exists
    # 2. start the task if it is not running
    return jsonify({"task": task_name}), 200


@bp.route("/tasks/<string:task_name>/stop", methods=["POST"])
def stop_task(task_name: str):
    # TODO:
    # 1. check the task exists
    # 2. stop the task if it is running
    return jsonify({"task": task_name}), 200


@bp.route("/tasks/<string:task_name>/status", methods=["GET"])
def task_status(task_name: str):
    # TODO:
    # 1. check the task exists
    # 2. get the task status
    return jsonify({"task": task_name}), 200


@bp.route("/tasks/<string:task_name>/results", methods=["GET"])
def task_results(task_name: str):
    # TODO:
    # 1. check the task exists
    # 2. get the task results
    return jsonify({"task": task_name}), 200
