from flask import jsonify
from . import admin_bp


@admin_bp.route('/')
def index():
    return jsonify({'module': 'admin', 'status': 'ok'})
