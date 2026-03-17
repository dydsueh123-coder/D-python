import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    # 개발환경 전용 폴백 — 운영에서는 절대 이 값 사용 금지
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-insecure-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # LDAP 설정 (leemock.local AD)
    LDAP_SERVER = os.environ.get('LDAP_SERVER', 'ldap://dc.leemock.local')
    LDAP_BASE_DN = os.environ.get('LDAP_BASE_DN', 'DC=leemock,DC=local')
    LDAP_USER_SEARCH_BASE = os.environ.get('LDAP_USER_SEARCH_BASE', 'OU=Users,DC=leemock,DC=local')

    # 파일 업로드
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB (화면 녹화)


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    # DB URL은 .env에서만 관리 — 하드코딩 금지
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
