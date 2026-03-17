from datetime import datetime
from flask_login import UserMixin
from app.extensions import db


class User(UserMixin, db.Model):
    """사용자 모델 — AD LDAP 캐시 + Flask-Login 세션용"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)  # AD sAMAccountName
    display_name = db.Column(db.String(100), nullable=False)           # AD displayName
    email = db.Column(db.String(200))                                   # AD mail
    department = db.Column(db.String(100))                              # AD department
    position = db.Column(db.String(100))                                # AD title
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


from app.extensions import login_manager  # noqa: E402 (순환 참조 방지용 지연 임포트)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
