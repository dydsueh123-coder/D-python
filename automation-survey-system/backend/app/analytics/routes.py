from flask import jsonify
from . import analytics_bp


@analytics_bp.route('/')
def index():
    return jsonify({'module': 'analytics', 'status': 'ok'})
