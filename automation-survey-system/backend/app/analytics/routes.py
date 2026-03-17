"""분석/통계 API"""
from flask import jsonify
from . import analytics_bp
from .services import AnalyticsService
from app.auth.decorators import admin_required, login_required


@analytics_bp.route('/dashboard', methods=['GET'])
@admin_required
def dashboard():
    """전체 대시보드 요약 통계"""
    return jsonify(AnalyticsService.get_dashboard_stats())


@analytics_bp.route('/priority', methods=['GET'])
@admin_required
def priority_ranking():
    """자동화 우선순위 랭킹 (활성/종료 설문 대상)"""
    return jsonify(AnalyticsService.get_priority_ranking())


@analytics_bp.route('/surveys/<int:survey_id>', methods=['GET'])
@admin_required
def survey_analytics(survey_id):
    """설문별 상세 통계 (질문별 응답 집계)"""
    result = AnalyticsService.get_survey_analytics(survey_id)
    if not result:
        return jsonify({'error': '설문을 찾을 수 없습니다.'}), 404
    return jsonify(result)
