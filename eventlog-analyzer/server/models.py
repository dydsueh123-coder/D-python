# server/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Collection(db.Model):
    """로그 수집 세션 — 클라이언트 온디맨드 또는 서버 모니터링 수집 1회"""
    __tablename__ = "collections"

    id = db.Column(db.Integer, primary_key=True)
    target_host = db.Column(db.String(255), nullable=False)  # IP 또는 호스트명
    target_name = db.Column(db.String(255))                  # 별칭 (선택)
    type = db.Column(db.String(10), nullable=False)          # 'client' | 'server'
    collected_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="pending")     # pending|success|failed
    error_msg = db.Column(db.Text)
    fetch_hours = db.Column(db.Integer, default=24)
    total_events = db.Column(db.Integer, default=0)

    events = db.relationship("Event", backref="collection", lazy="dynamic",
                             cascade="all, delete-orphan")


class Event(db.Model):
    """개별 이벤트 로그 레코드"""
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey("collections.id"), nullable=False)
    event_id = db.Column(db.Integer, nullable=False)
    source_name = db.Column(db.String(255))
    log_type = db.Column(db.String(20))       # System|Application|Security
    level = db.Column(db.Integer)             # 1=Critical 2=Error 3=Warning 4=Info
    level_name = db.Column(db.String(20))
    time_generated = db.Column(db.DateTime)
    message = db.Column(db.Text)
    # 분류 결과
    category = db.Column(db.String(100))      # e.g. "비정상 종료", "BSOD", "디스크 오류"
    is_known_issue = db.Column(db.Boolean, default=False)
    resolution_hint = db.Column(db.Text)


class Server(db.Model):
    """모니터링 서버 등록 목록"""
    __tablename__ = "servers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)         # 표시 이름
    hostname_or_ip = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    watch_event_ids = db.relationship("WatchEventId", backref="server", lazy="dynamic",
                                      cascade="all, delete-orphan")


class WatchEventId(db.Model):
    """서버별 감시할 Event ID 목록"""
    __tablename__ = "watch_event_ids"

    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey("servers.id"), nullable=False)
    event_id = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255))  # e.g. "비정상 종료"
    severity = db.Column(db.String(20), default="warning")  # critical|warning|info
