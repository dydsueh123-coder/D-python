"""관리자 서비스 - 사용자 관리"""
from app.extensions import db
from app.auth.models import User
import logging

logger = logging.getLogger(__name__)


class AdminService:

    @staticmethod
    def list_users(page: int = 1, per_page: int = 30) -> dict:
        pagination = User.query.order_by(User.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        return {
            'items': pagination.items,
            'total': pagination.total,
            'page': page,
            'pages': pagination.pages,
        }

    @staticmethod
    def set_admin(user_id: int, is_admin: bool) -> User | None:
        user = User.query.get(user_id)
        if not user:
            return None
        user.is_admin = is_admin
        db.session.commit()
        logger.info(f"Admin status changed: user={user.username} is_admin={is_admin}")
        return user

    @staticmethod
    def user_to_dict(user: User) -> dict:
        return {
            'id': user.id,
            'username': user.username,
            'display_name': user.display_name,
            'email': user.email,
            'department': user.department,
            'position': user.position,
            'is_admin': user.is_admin,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'created_at': user.created_at.isoformat(),
        }
