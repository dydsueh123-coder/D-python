"""설문 CRUD 및 상태 전환 테스트"""
import pytest


class TestSurveyCreate:
    def test_create_survey_as_admin(self, admin_client):
        resp = admin_client.post('/api/surveys/', json={
            'title': '새 설문', 'description': '설명'
        })
        assert resp.status_code == 201
        data = resp.json
        assert data['title'] == '새 설문'
        assert data['status'] == 'draft'

    def test_create_survey_requires_title(self, admin_client):
        resp = admin_client.post('/api/surveys/', json={'description': '제목없음'})
        assert resp.status_code == 400

    def test_create_survey_forbidden_for_normal_user(self, user_client):
        resp = user_client.post('/api/surveys/', json={'title': '권한없음'})
        assert resp.status_code == 403

    def test_create_survey_requires_login(self, client):
        resp = client.post('/api/surveys/', json={'title': '미로그인'})
        assert resp.status_code == 401


class TestSurveyRead:
    def test_list_surveys(self, user_client, draft_survey):
        resp = user_client.get('/api/surveys/')
        assert resp.status_code == 200
        assert resp.json['total'] >= 1

    def test_list_surveys_status_filter(self, user_client, draft_survey):
        resp = user_client.get('/api/surveys/?status=draft')
        assert resp.status_code == 200
        for item in resp.json['items']:
            assert item['status'] == 'draft'

    def test_get_survey_includes_questions(self, user_client, survey_with_questions):
        resp = user_client.get(f'/api/surveys/{survey_with_questions.id}')
        assert resp.status_code == 200
        assert 'questions' in resp.json
        assert len(resp.json['questions']) == 3

    def test_get_survey_not_found(self, user_client):
        resp = user_client.get('/api/surveys/99999')
        assert resp.status_code == 404


class TestSurveyUpdate:
    def test_update_survey_title(self, admin_client, draft_survey):
        resp = admin_client.put(f'/api/surveys/{draft_survey.id}', json={'title': '수정된 제목'})
        assert resp.status_code == 200
        assert resp.json['title'] == '수정된 제목'

    def test_cannot_update_closed_survey(self, admin_client, db, active_survey):
        active_survey.status = 'closed'
        db.session.commit()
        resp = admin_client.put(f'/api/surveys/{active_survey.id}', json={'title': '수정시도'})
        assert resp.status_code == 400


class TestSurveyDelete:
    def test_delete_draft_survey(self, admin_client, draft_survey):
        resp = admin_client.delete(f'/api/surveys/{draft_survey.id}')
        assert resp.status_code == 200

    def test_cannot_delete_active_survey(self, admin_client, active_survey):
        resp = admin_client.delete(f'/api/surveys/{active_survey.id}')
        assert resp.status_code == 400


class TestSurveyStateTransition:
    def test_activate_survey(self, admin_client, survey_with_questions):
        resp = admin_client.post(f'/api/surveys/{survey_with_questions.id}/activate')
        assert resp.status_code == 200
        assert resp.json['status'] == 'active'

    def test_cannot_activate_without_questions(self, admin_client, draft_survey):
        resp = admin_client.post(f'/api/surveys/{draft_survey.id}/activate')
        assert resp.status_code == 400

    def test_close_active_survey(self, admin_client, active_survey):
        resp = admin_client.post(f'/api/surveys/{active_survey.id}/close')
        assert resp.status_code == 200
        assert resp.json['status'] == 'closed'

    def test_cannot_activate_already_active(self, admin_client, active_survey):
        resp = admin_client.post(f'/api/surveys/{active_survey.id}/activate')
        assert resp.status_code == 400

    def test_cannot_close_draft_survey(self, admin_client, survey_with_questions):
        resp = admin_client.post(f'/api/surveys/{survey_with_questions.id}/close')
        assert resp.status_code == 400


class TestQuestionManagement:
    def test_add_question(self, admin_client, draft_survey):
        resp = admin_client.post(f'/api/surveys/{draft_survey.id}/questions', json={
            'question_type': 'text',
            'question_text': '새 질문',
            'is_required': True,
        })
        assert resp.status_code == 201
        assert resp.json['question_text'] == '새 질문'

    def test_add_radio_question_requires_options(self, admin_client, draft_survey):
        resp = admin_client.post(f'/api/surveys/{draft_survey.id}/questions', json={
            'question_type': 'radio',
            'question_text': '선택지 없는 라디오',
        })
        assert resp.status_code == 400

    def test_cannot_add_question_to_active_survey(self, admin_client, active_survey):
        resp = admin_client.post(f'/api/surveys/{active_survey.id}/questions', json={
            'question_type': 'text', 'question_text': '질문추가시도',
        })
        assert resp.status_code == 400

    def test_delete_question(self, admin_client, survey_with_questions):
        questions = survey_with_questions.questions.all()
        q_id = questions[0].id
        resp = admin_client.delete(
            f'/api/surveys/{survey_with_questions.id}/questions/{q_id}'
        )
        assert resp.status_code == 200

    def test_reorder_questions(self, admin_client, survey_with_questions):
        questions = survey_with_questions.questions.order_by('order_num').all()
        new_order = [
            {'id': questions[0].id, 'order_num': 3},
            {'id': questions[1].id, 'order_num': 1},
            {'id': questions[2].id, 'order_num': 2},
        ]
        resp = admin_client.put(
            f'/api/surveys/{survey_with_questions.id}/questions/reorder',
            json=new_order,
        )
        assert resp.status_code == 200
