from flask import jsonify


def bad_request(e):
    return jsonify(error=str(e)), 400


def internal_server_error(e):
    return jsonify(error=str(e)), 500


def not_implemented(e):
    return jsonify(error=str(e)), 500
