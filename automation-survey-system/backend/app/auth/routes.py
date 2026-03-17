from flask import jsonify
from . import auth_bp


@auth_bp.route('/')
def index():
    return jsonify({'module': 'auth', 'status': 'ok'})
