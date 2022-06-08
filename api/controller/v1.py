from flask import Blueprint, request, jsonify

bp = Blueprint('v1', __name__, url_prefix='/v1')

@bp.route('/version', methods=['GET'])
def index():
    return 200, jsonify({'version': '1.0'})

