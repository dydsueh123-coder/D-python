"""분석/통계 API 테스트"""
from app.surveys.models import SurveyResponse, Answer


def _submit_response(db, survey, user, answers_data):
    """테스트용 응답 직접 생성"""
    from datetime import datetime, timezone
    response = SurveyResponse(
        survey_id=survey.id, user_id=user.id,
        submitted_at=datetime.now(timezone.utc), is_complete=True,
    )
    db.session.add(response)
    db.session.flush()
    for a in answers_data:
        db.session.add(Answer(
            response_id=response.id,
            question_id=a['question_id'],
            answer_text=a.get('answer_text'),
            answer_data=a.get('answer_data'),
        ))
    db.session.commit()
    return response


class TestDashboard:
    def test_dashboard_requires_admin(self, user_client):
        resp = user_client.get('/api/analytics/dashboard')
        assert resp.status_code == 403

    def test_dashboard_stats(self, admin_client, active_survey):
        resp = admin_client.get('/api/analytics/dashboard')
        assert resp.status_code == 200
        data = resp.json
        assert 'total_surveys' in data
        assert 'active_surveys' in data
        assert data['active_surveys'] >= 1

    def test_dashboard_counts_active_surveys(self, admin_client, active_survey):
        # active_survey 픽스처가 draft→active 전환하므로 active_surveys >= 1
        resp = admin_client.get('/api/analytics/dashboard')
        assert resp.status_code == 200
        data = resp.json
        assert data['active_surveys'] >= 1
        assert data['total_surveys'] >= 1


class TestPriorityRanking:
    def test_priority_ranking_empty(self, admin_client):
        resp = admin_client.get('/api/analytics/priority')
        assert resp.status_code == 200
        assert isinstance(resp.json, list)

    def test_priority_ranking_with_responses(self, admin_client, db, active_survey, normal_user):
        questions = active_survey.questions.all()
        scale_q = next((q for q in questions if q.question_type == 'scale'), None)
        if scale_q:
            _submit_response(db, active_survey, normal_user, [
                {'question_id': scale_q.id, 'answer_data': 4},
                *[{'question_id': q.id, 'answer_text': 'x'} for q in questions
                  if q.id != scale_q.id and q.question_type in ('text', 'textarea')],
            ])

        resp = admin_client.get('/api/analytics/priority')
        assert resp.status_code == 200
        items = resp.json
        # 랭킹 순서 확인
        for i, item in enumerate(items):
            assert item['priority_rank'] == i + 1

    def test_priority_ranking_requires_admin(self, user_client):
        resp = user_client.get('/api/analytics/priority')
        assert resp.status_code == 403


class TestSurveyAnalytics:
    def test_survey_analytics_not_found(self, admin_client):
        resp = admin_client.get('/api/analytics/surveys/99999')
        assert resp.status_code == 404

    def test_survey_analytics_structure(self, admin_client, active_survey):
        resp = admin_client.get(f'/api/analytics/surveys/{active_survey.id}')
        assert resp.status_code == 200
        data = resp.json
        assert data['survey_id'] == active_survey.id
        assert 'questions' in data
        assert 'total_responses' in data

    def test_survey_analytics_with_scale_responses(
        self, admin_client, db, active_survey, normal_user
    ):
        questions = active_survey.questions.all()
        scale_q = next((q for q in questions if q.question_type == 'scale'), None)
        text_qs = [q for q in questions if q.question_type in ('text', 'textarea')]

        if scale_q:
            _submit_response(db, active_survey, normal_user, [
                {'question_id': scale_q.id, 'answer_data': 5},
                *[{'question_id': q.id, 'answer_text': '응답'} for q in text_qs],
            ])

        resp = admin_client.get(f'/api/analytics/surveys/{active_survey.id}')
        assert resp.status_code == 200
        data = resp.json
        assert data['total_responses'] == 1

        if scale_q:
            q_stat = next(
                (q for q in data['questions'] if q['question_type'] == 'scale'), None
            )
            assert q_stat is not None
            assert q_stat['stats']['avg'] == 5.0
