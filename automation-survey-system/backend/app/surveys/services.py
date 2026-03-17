"""설문 관리 비즈니스 로직"""
from datetime import datetime, timezone
from app.extensions import db
from .models import Survey, Question, SurveyResponse, Answer
import logging

logger = logging.getLogger(__name__)


class SurveyService:

    # ── 설문 CRUD ──────────────────────────────────────────

    @staticmethod
    def create_survey(creator_id: int, data: dict) -> Survey:
        survey = Survey(
            title=data['title'],
            description=data.get('description'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            created_by=creator_id,
            status='draft',
        )
        db.session.add(survey)
        db.session.commit()
        logger.info(f"Survey created: id={survey.id} by user={creator_id}")
        return survey

    @staticmethod
    def get_survey(survey_id: int) -> Survey | None:
        return Survey.query.get(survey_id)

    @staticmethod
    def list_surveys(status: str | None = None, page: int = 1, per_page: int = 20) -> dict:
        q = Survey.query.order_by(Survey.created_at.desc())
        if status:
            q = q.filter_by(status=status)
        pagination = q.paginate(page=page, per_page=per_page, error_out=False)
        return {
            'items': pagination.items,
            'total': pagination.total,
            'page': page,
            'pages': pagination.pages,
        }

    @staticmethod
    def update_survey(survey: Survey, data: dict) -> Survey:
        if survey.status == 'closed':
            raise ValueError("종료된 설문은 수정할 수 없습니다.")
        for field in ('title', 'description', 'start_date', 'end_date'):
            if field in data:
                setattr(survey, field, data[field])
        db.session.commit()
        return survey

    @staticmethod
    def delete_survey(survey: Survey) -> None:
        if survey.status == 'active':
            raise ValueError("활성 설문은 삭제할 수 없습니다. 먼저 종료하세요.")
        db.session.delete(survey)
        db.session.commit()
        logger.info(f"Survey deleted: id={survey.id}")

    # ── 상태 전환 ──────────────────────────────────────────

    @staticmethod
    def activate_survey(survey: Survey) -> Survey:
        if survey.status != 'draft':
            raise ValueError(f"초안(draft) 상태에서만 활성화할 수 있습니다. 현재: {survey.status}")
        if survey.questions.count() == 0:
            raise ValueError("질문이 없는 설문은 활성화할 수 없습니다.")
        survey.status = 'active'
        db.session.commit()
        logger.info(f"Survey activated: id={survey.id}")
        return survey

    @staticmethod
    def close_survey(survey: Survey) -> Survey:
        if survey.status != 'active':
            raise ValueError(f"활성(active) 상태에서만 종료할 수 있습니다. 현재: {survey.status}")
        survey.status = 'closed'
        db.session.commit()
        logger.info(f"Survey closed: id={survey.id}")
        return survey

    # ── 질문 관리 ──────────────────────────────────────────

    VALID_QUESTION_TYPES = {'text', 'textarea', 'radio', 'checkbox', 'scale', 'file'}

    @classmethod
    def add_question(cls, survey: Survey, data: dict) -> Question:
        if survey.status != 'draft':
            raise ValueError("초안(draft) 상태의 설문만 질문을 추가할 수 있습니다.")
        q_type = data.get('question_type')
        if q_type not in cls.VALID_QUESTION_TYPES:
            raise ValueError(f"유효하지 않은 질문 유형: {q_type}. 허용값: {cls.VALID_QUESTION_TYPES}")
        if q_type in ('radio', 'checkbox') and not data.get('options'):
            raise ValueError("radio/checkbox 질문은 options 필드가 필요합니다.")

        max_order = db.session.query(db.func.max(Question.order_num))\
            .filter_by(survey_id=survey.id).scalar() or 0

        question = Question(
            survey_id=survey.id,
            question_type=q_type,
            question_text=data['question_text'],
            is_required=data.get('is_required', True),
            options=data.get('options'),
            order_num=max_order + 1,
        )
        db.session.add(question)
        db.session.commit()
        return question

    @staticmethod
    def update_question(survey: Survey, question: Question, data: dict) -> Question:
        if survey.status != 'draft':
            raise ValueError("초안(draft) 상태의 설문만 질문을 수정할 수 있습니다.")
        for field in ('question_text', 'is_required', 'options', 'question_type'):
            if field in data:
                setattr(question, field, data[field])
        db.session.commit()
        return question

    @staticmethod
    def delete_question(survey: Survey, question: Question) -> None:
        if survey.status != 'draft':
            raise ValueError("초안(draft) 상태의 설문만 질문을 삭제할 수 있습니다.")
        db.session.delete(question)
        db.session.commit()

    @staticmethod
    def reorder_questions(survey: Survey, order_list: list) -> list:
        """order_list: [{'id': 1, 'order_num': 1}, ...]"""
        if survey.status != 'draft':
            raise ValueError("초안(draft) 상태의 설문만 순서를 변경할 수 있습니다.")
        id_to_order = {item['id']: item['order_num'] for item in order_list}
        questions = Question.query.filter_by(survey_id=survey.id).all()
        for q in questions:
            if q.id in id_to_order:
                q.order_num = id_to_order[q.id]
        db.session.commit()
        return sorted(questions, key=lambda q: q.order_num)

    # ── 응답 제출 ──────────────────────────────────────────

    @staticmethod
    def submit_response(survey: Survey, user_id: int, answers_data: list) -> SurveyResponse:
        if survey.status != 'active':
            raise ValueError("활성(active) 상태의 설문에만 응답할 수 있습니다.")

        # 중복 응답 방지
        existing = SurveyResponse.query.filter_by(
            survey_id=survey.id, user_id=user_id, is_complete=True
        ).first()
        if existing:
            raise ValueError("이미 응답한 설문입니다.")

        # 필수 질문 체크
        required_ids = {
            q.id for q in Question.query.filter_by(survey_id=survey.id, is_required=True).all()
        }
        answered_ids = {a['question_id'] for a in answers_data}
        missing = required_ids - answered_ids
        if missing:
            raise ValueError(f"필수 질문에 답변하지 않았습니다. question_id={sorted(missing)}")

        response = SurveyResponse(
            survey_id=survey.id,
            user_id=user_id,
            submitted_at=datetime.now(timezone.utc),
            is_complete=True,
        )
        db.session.add(response)
        db.session.flush()  # response.id 확보

        for a in answers_data:
            db.session.add(Answer(
                response_id=response.id,
                question_id=a['question_id'],
                answer_text=a.get('answer_text'),
                answer_data=a.get('answer_data'),
            ))

        db.session.commit()
        logger.info(f"Response submitted: survey={survey.id} user={user_id} response={response.id}")
        return response

    @staticmethod
    def get_my_response(survey_id: int, user_id: int) -> SurveyResponse | None:
        return SurveyResponse.query.filter_by(
            survey_id=survey_id, user_id=user_id, is_complete=True
        ).first()

    @staticmethod
    def list_responses(survey_id: int) -> list:
        return SurveyResponse.query.filter_by(survey_id=survey_id, is_complete=True)\
            .order_by(SurveyResponse.submitted_at.desc()).all()
