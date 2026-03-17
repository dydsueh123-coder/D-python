import pytest
from app import create_app
from app.extensions import db as _db
from app.auth.models import User
from app.surveys.models import Survey, Question, SurveyResponse, Answer


@pytest.fixture
def app():
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'UPLOAD_FOLDER': '/tmp/tass_test_uploads',
        'WTF_CSRF_ENABLED': False,
    })
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def admin_user(db):
    user = User(
        username='admin', display_name='관리자',
        email='admin@test.local', is_admin=True,
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def normal_user(db):
    user = User(
        username='user1', display_name='일반사용자',
        email='user1@test.local', is_admin=False,
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_client(client, admin_user):
    """관리자로 로그인된 테스트 클라이언트"""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(admin_user.id)
        sess['_fresh'] = True
    return client


@pytest.fixture
def user_client(client, normal_user):
    """일반 사용자로 로그인된 테스트 클라이언트"""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(normal_user.id)
        sess['_fresh'] = True
    return client


@pytest.fixture
def draft_survey(db, admin_user):
    """초안 상태 설문 (질문 없음)"""
    survey = Survey(
        title='테스트 설문', description='테스트용',
        status='draft', created_by=admin_user.id,
    )
    db.session.add(survey)
    db.session.commit()
    return survey


@pytest.fixture
def survey_with_questions(db, draft_survey):
    """질문이 있는 초안 설문"""
    q1 = Question(
        survey_id=draft_survey.id, order_num=1,
        question_type='text', question_text='업무 이름을 입력하세요.',
        is_required=True,
    )
    q2 = Question(
        survey_id=draft_survey.id, order_num=2,
        question_type='scale', question_text='자동화 필요성은?',
        is_required=True,
    )
    q3 = Question(
        survey_id=draft_survey.id, order_num=3,
        question_type='radio', question_text='주기는?',
        is_required=False,
        options=['매일', '매주', '매월'],
    )
    db.session.add_all([q1, q2, q3])
    db.session.commit()
    return draft_survey


@pytest.fixture
def active_survey(db, survey_with_questions):
    """활성 설문"""
    survey_with_questions.status = 'active'
    db.session.commit()
    return survey_with_questions
