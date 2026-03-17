import os
from datetime import timedelta
from flask import Flask
from .config import config_by_name
from .extensions import db, migrate, login_manager, cors


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # 운영환경 필수 환경변수 검증
    if config_name == 'production':
        if not os.environ.get('SECRET_KEY'):
            raise ValueError("운영환경: SECRET_KEY 환경변수 필수")
        if not os.environ.get('DATABASE_URL'):
            raise ValueError("운영환경: DATABASE_URL 환경변수 필수")

    # 익스텐션 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    cors.init_app(app, origins=['http://localhost:5173'])  # Vite dev server

    # Flask-Login 설정
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '로그인이 필요합니다.'

    # 세션 수명 설정 (8시간)
    app.permanent_session_lifetime = timedelta(hours=8)

    # 모델 임포트 (Alembic 자동 감지용)
    from .auth import models as auth_models  # noqa
    from .surveys import models as survey_models  # noqa
    from .recordings import models as recording_models  # noqa

    # Blueprint 등록
    from .auth import auth_bp
    from .surveys import surveys_bp
    from .recordings import recordings_bp
    from .analytics import analytics_bp
    from .admin import admin_bp
    from .common.errors import register_error_handlers

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(surveys_bp, url_prefix='/api/surveys')
    app.register_blueprint(recordings_bp, url_prefix='/api/recordings')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    register_error_handlers(app)

    # 헬스체크
    @app.route('/api/health')
    def health():
        return {'status': 'ok'}

    return app
