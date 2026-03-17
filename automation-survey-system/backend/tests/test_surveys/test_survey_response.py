"""설문 응답 제출 테스트"""
import pytest
from app.surveys.models import Question


class TestSubmitResponse:
    def _make_answers(self, survey):
        """설문의 질문에 맞는 유효한 응답 생성"""
        answers = []
        for q in survey.questions.all():
            if q.question_type in ('text', 'textarea'):
                answers.append({'question_id': q.id, 'answer_text': '테스트 답변'})
            else:
                answers.append({'question_id': q.id, 'answer_data': 3})
        return answers

    def test_submit_response(self, user_client, active_survey):
        answers = self._make_answers(active_survey)
        resp = user_client.post(
            f'/api/surveys/{active_survey.id}/responses',
            json={'answers': answers},
        )
        assert resp.status_code == 201
        assert resp.json['is_complete'] is True

    def test_cannot_respond_to_draft_survey(self, user_client, survey_with_questions):
        resp = user_client.post(
            f'/api/surveys/{survey_with_questions.id}/responses',
            json={'answers': []},
        )
        assert resp.status_code == 400

    def test_duplicate_response_rejected(self, user_client, active_survey):
        answers = self._make_answers(active_survey)
        user_client.post(
            f'/api/surveys/{active_survey.id}/responses',
            json={'answers': answers},
        )
        # 두 번째 제출
        resp = user_client.post(
            f'/api/surveys/{active_survey.id}/responses',
            json={'answers': answers},
        )
        assert resp.status_code == 400
        assert '이미 응답' in resp.json['error']

    def test_missing_required_question_rejected(self, user_client, active_survey):
        # 필수 질문을 빠뜨리고 제출
        resp = user_client.post(
            f'/api/surveys/{active_survey.id}/responses',
            json={'answers': []},
        )
        assert resp.status_code == 400
        assert '필수 질문' in resp.json['error']

    def test_get_my_response(self, user_client, active_survey):
        answers = self._make_answers(active_survey)
        user_client.post(
            f'/api/surveys/{active_survey.id}/responses',
            json={'answers': answers},
        )
        resp = user_client.get(f'/api/surveys/{active_survey.id}/responses/mine')
        assert resp.status_code == 200
        assert resp.json['is_complete'] is True
        assert 'answers' in resp.json

    def test_get_my_response_not_found(self, user_client, active_survey):
        resp = user_client.get(f'/api/surveys/{active_survey.id}/responses/mine')
        assert resp.status_code == 404

    def test_list_responses_forbidden_for_normal_user(self, user_client, active_survey):
        # 일반 유저는 전체 응답 목록 접근 불가
        resp = user_client.get(f'/api/surveys/{active_survey.id}/responses')
        assert resp.status_code == 403

    def test_list_responses_allowed_for_admin(self, admin_client, active_survey):
        # 관리자는 접근 가능
        resp = admin_client.get(f'/api/surveys/{active_survey.id}/responses')
        assert resp.status_code == 200
