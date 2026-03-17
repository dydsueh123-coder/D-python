from flask import request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timezone

from . import auth_bp
from .models import User
from .ldap_service import ldap_service
from app.extensions import db
import logging

logger = logging.getLogger(__name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """AD LDAP 로그인"""
    data = request.get_json()
    if not data:
        return jsonify({'error': '요청 데이터가 없습니다.'}), 400

    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'error': '사용자명과 비밀번호를 입력하세요.'}), 400

    # LDAP 인증
    success, result = ldap_service.authenticate(username, password)
    if not success:
        return jsonify({'error': result}), 401

    # DB에 사용자 upsert (LDAP 캐시)
    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(username=username)
        db.session.add(user)

    user.display_name = result['display_name']
    user.email = result.get('email')
    user.department = result.get('department')
    user.position = result.get('position')
    user.last_login = datetime.now(timezone.utc)
    db.session.commit()

    # Flask-Login 세션 등록
    login_user(user, remember=False)
    session.permanent = True

    logger.info(f"Login success: {username} ({user.department})")
    return jsonify({
        'message': '로그인 성공',
        'user': _user_to_dict(user)
    })


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """로그아웃"""
    username = current_user.username
    logout_user()
    logger.info(f"Logout: {username}")
    return jsonify({'message': '로그아웃 되었습니다.'})


@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    """현재 로그인 사용자 정보"""
    return jsonify(_user_to_dict(current_user))


def _user_to_dict(user: User) -> dict:
    return {
        'id': user.id,
        'username': user.username,
        'display_name': user.display_name,
        'email': user.email,
        'department': user.department,
        'position': user.position,
        'is_admin': user.is_admin,
    }
