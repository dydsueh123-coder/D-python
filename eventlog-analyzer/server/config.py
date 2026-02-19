# server/config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin1234")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(DATA_DIR, 'eventlog.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 로그 수집 기본값
    DEFAULT_FETCH_HOURS = 24        # 최근 N시간
    DEFAULT_MAX_EVENTS = 200        # 최대 이벤트 수
    LOG_TYPES = ["System", "Application", "Security"]
    PORT_RPC = 135
    PORT_WINRM = 5985
    PORT_TIMEOUT = 2.0
