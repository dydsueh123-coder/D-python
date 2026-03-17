from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
cors = CORS()


@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({'error': '로그인이 필요합니다.'}), 401
