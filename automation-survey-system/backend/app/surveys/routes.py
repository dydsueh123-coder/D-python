from flask import jsonify
from . import surveys_bp


@surveys_bp.route('/')
def index():
    return jsonify({'module': 'surveys', 'status': 'ok'})
