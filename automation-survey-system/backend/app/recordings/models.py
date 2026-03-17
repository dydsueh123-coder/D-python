from datetime import datetime
from app.extensions import db


class Recording(db.Model):
    """화면 녹화 파일"""
    __tablename__ = 'recordings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    survey_response_id = db.Column(db.Integer, db.ForeignKey('survey_responses.id'))
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255))
    file_size = db.Column(db.BigInteger)  # bytes
    duration_seconds = db.Column(db.Integer)
    status = db.Column(db.String(20), default='uploaded', nullable=False)
    # 상태: uploaded, processing, ready, error
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Recording {self.id}: {self.filename}>'
