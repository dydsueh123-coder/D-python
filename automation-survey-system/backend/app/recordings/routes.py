from flask import jsonify
from . import recordings_bp


@recordings_bp.route('/')
def index():
    return jsonify({'module': 'recordings', 'status': 'ok'})
