"""설문 관리 API 라우트 - Phase 3"""
from flask import request, jsonify
from flask_login import login_required, current_user

from . import surveys_bp
from .models import Question
from .services import SurveyService
from .schemas import survey_to_dict, question_to_dict, response_to_dict
from app.auth.decorators import admin_required
import logging

logger = logging.getLogger(__name__)


# ── 헬퍼 ──────────────────────────────────────────────────

def _get_survey_or_404(survey_id: int):
    survey = SurveyService.get_survey(survey_id)
    if not survey:
        return None, (jsonify({'error': '설문을 찾을 수 없습니다.'}), 404)
    return survey, None


def _get_question_or_404(survey, question_id: int):
    question = Question.query.filter_by(id=question_id, survey_id=survey.id).first()
    if not question:
        return None, (jsonify({'error': '질문을 찾을 수 없습니다.'}), 404)
    return question, None


# ── 설문 CRUD ──────────────────────────────────────────────

@surveys_bp.route('/', methods=['GET'])
@login_required
def list_surveys():
    """설문 목록 조회 (status 필터, 페이징)"""
    status = request.args.get('status')
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)

    result = SurveyService.list_surveys(status=status, page=page, per_page=per_page)
    return jsonify({
        'items': [survey_to_dict(s) for s in result['items']],
        'total': result['total'],
        'page': result['page'],
        'pages': result['pages'],
    })


@surveys_bp.route('/', methods=['POST'])
@login_required
def create_survey():
    """설문 생성 (관리자만)"""
    if not current_user.is_admin:
        return jsonify({'error': '설문 생성 권한이 없습니다.'}), 403

    data = request.get_json()
    if not data or not data.get('title'):
        return jsonify({'error': 'title 필드는 필수입니다.'}), 400

    try:
        survey = SurveyService.create_survey(creator_id=current_user.id, data=data)
        return jsonify(survey_to_dict(survey)), 201
    except Exception as e:
        logger.exception("설문 생성 오류")
        return jsonify({'error': str(e)}), 500


@surveys_bp.route('/<int:survey_id>', methods=['GET'])
@login_required
def get_survey(survey_id):
    """설문 상세 조회 (질문 목록 포함)"""
    survey, err = _get_survey_or_404(survey_id)
    if err:
        return err
    return jsonify(survey_to_dict(survey, include_questions=True))


@surveys_bp.route('/<int:survey_id>', methods=['PUT'])
@login_required
def update_survey(survey_id):
    """설문 수정 (관리자만)"""
    if not current_user.is_admin:
        return jsonify({'error': '설문 수정 권한이 없습니다.'}), 403

    survey, err = _get_survey_or_404(survey_id)
    if err:
        return err

    data = request.get_json() or {}
    try:
        survey = SurveyService.update_survey(survey, data)
        return jsonify(survey_to_dict(survey))
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@surveys_bp.route('/<int:survey_id>', methods=['DELETE'])
@admin_required
def delete_survey(survey_id):
    """설문 삭제 (관리자만, 활성 설문 삭제 불가)"""
    survey, err = _get_survey_or_404(survey_id)
    if err:
        return err

    try:
        SurveyService.delete_survey(survey)
        return jsonify({'message': '삭제되었습니다.'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


# ── 상태 전환 ──────────────────────────────────────────────

@surveys_bp.route('/<int:survey_id>/activate', methods=['POST'])
@admin_required
def activate_survey(survey_id):
    """설문 활성화 draft → active"""
    survey, err = _get_survey_or_404(survey_id)
    if err:
        return err

    try:
        survey = SurveyService.activate_survey(survey)
        return jsonify(survey_to_dict(survey))
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@surveys_bp.route('/<int:survey_id>/close', methods=['POST'])
@admin_required
def close_survey(survey_id):
    """설문 종료 active → closed"""
    survey, err = _get_survey_or_404(survey_id)
    if err:
        return err

    try:
        survey = SurveyService.close_survey(survey)
        return jsonify(survey_to_dict(survey))
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


# ── 질문 관리 ──────────────────────────────────────────────

@surveys_bp.route('/<int:survey_id>/questions', methods=['POST'])
@admin_required
def add_question(survey_id):
    """질문 추가 (draft 상태만)"""
    survey, err = _get_survey_or_404(survey_id)
    if err:
        return err

    data = request.get_json() or {}
    if not data.get('question_text') or not data.get('question_type'):
        return jsonify({'error': 'question_text, question_type 필드는 필수입니다.'}), 400

    try:
        question = SurveyService.add_question(survey, data)
        return jsonify(question_to_dict(question)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@surveys_bp.route('/<int:survey_id>/questions/<int:question_id>', methods=['PUT'])
@admin_required
def update_question(survey_id, question_id):
    """질문 수정 (draft 상태만)"""
    survey, err = _get_survey_or_404(survey_id)
    if err:
        return err
    question, err = _get_question_or_404(survey, question_id)
    if err:
        return err

    data = request.get_json() or {}
    try:
        question = SurveyService.update_question(survey, question, data)
        return jsonify(question_to_dict(question))
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@surveys_bp.route('/<int:survey_id>/questions/<int:question_id>', methods=['DELETE'])
@admin_required
def delete_question(survey_id, question_id):
    """질문 삭제 (draft 상태만)"""
    survey, err = _get_survey_or_404(survey_id)
    if err:
        return err
    question, err = _get_question_or_404(survey, question_id)
    if err:
        return err

    try:
        SurveyService.delete_question(survey, question)
        return jsonify({'message': '질문이 삭제되었습니다.'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@surveys_bp.route('/<int:survey_id>/questions/reorder', methods=['PUT'])
@admin_required
def reorder_questions(survey_id):
    """질문 순서 변경 - body: [{'id': 1, 'order_num': 1}, ...]"""
    survey, err = _get_survey_or_404(survey_id)
    if err:
        return err

    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({'error': '요청 body는 배열이어야 합니다.'}), 400

    try:
        questions = SurveyService.reorder_questions(survey, data)
        return jsonify([question_to_dict(q) for q in questions])
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


# ── 설문 응답 ──────────────────────────────────────────────

@surveys_bp.route('/<int:survey_id>/responses', methods=['POST'])
@login_required
def submit_response(survey_id):
    """설문 응답 제출 (active 설문, 중복 불가)"""
    survey, err = _get_survey_or_404(survey_id)
    if err:
        return err

    data = request.get_json() or {}
    answers_data = data.get('answers', [])
    if not isinstance(answers_data, list):
        return jsonify({'error': 'answers 필드는 배열이어야 합니다.'}), 400

    try:
        response = SurveyService.submit_response(survey, current_user.id, answers_data)
        return jsonify(response_to_dict(response, include_answers=True)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@surveys_bp.route('/<int:survey_id>/responses/mine', methods=['GET'])
@login_required
def get_my_response(survey_id):
    """내 응답 조회"""
    survey, err = _get_survey_or_404(survey_id)
    if err:
        return err

    response = SurveyService.get_my_response(survey_id, current_user.id)
    if not response:
        return jsonify({'error': '응답 내역이 없습니다.'}), 404
    return jsonify(response_to_dict(response, include_answers=True))


@surveys_bp.route('/<int:survey_id>/responses', methods=['GET'])
@admin_required
def list_responses(survey_id):
    """응답 목록 조회 (관리자만)"""
    survey, err = _get_survey_or_404(survey_id)
    if err:
        return err

    responses = SurveyService.list_responses(survey_id)
    return jsonify({
        'survey_id': survey_id,
        'total': len(responses),
        'items': [response_to_dict(r) for r in responses],
    })
