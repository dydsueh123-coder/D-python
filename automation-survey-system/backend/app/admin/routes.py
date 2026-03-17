"""관리자 API - 사용자 관리"""
from flask import request, jsonify
from flask_login import current_user
from . import admin_bp
from .services import AdminService
from app.auth.decorators import admin_required


@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 30)), 100)
    result = AdminService.list_users(page=page, per_page=per_page)
    return jsonify({
        'items': [AdminService.user_to_dict(u) for u in result['items']],
        'total': result['total'],
        'page': result['page'],
        'pages': result['pages'],
    })


@admin_bp.route('/users/<int:user_id>/admin', methods=['PUT'])
@admin_required
def set_admin(user_id):
    """관리자 권한 부여/해제"""
    if user_id == current_user.id:
        return jsonify({'error': '자신의 관리자 권한은 변경할 수 없습니다.'}), 400

    data = request.get_json() or {}
    is_admin = bool(data.get('is_admin', False))

    user = AdminService.set_admin(user_id, is_admin)
    if not user:
        return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
    return jsonify(AdminService.user_to_dict(user))
