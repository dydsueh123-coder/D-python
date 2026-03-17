"""설문 직렬화 헬퍼 (marshmallow 없이 dict 변환)"""
from .models import Survey, Question, SurveyResponse, Answer


def survey_to_dict(survey: Survey, include_questions: bool = False) -> dict:
    data = {
        'id': survey.id,
        'title': survey.title,
        'description': survey.description,
        'status': survey.status,
        'created_by': survey.created_by,
        'start_date': survey.start_date.isoformat() if survey.start_date else None,
        'end_date': survey.end_date.isoformat() if survey.end_date else None,
        'created_at': survey.created_at.isoformat(),
        'updated_at': survey.updated_at.isoformat(),
        'question_count': survey.questions.count(),
        'response_count': survey.responses.count(),
    }
    if include_questions:
        questions = survey.questions.order_by(Question.order_num).all()
        data['questions'] = [question_to_dict(q) for q in questions]
    return data


def question_to_dict(question: Question) -> dict:
    return {
        'id': question.id,
        'survey_id': question.survey_id,
        'order_num': question.order_num,
        'question_type': question.question_type,
        'question_text': question.question_text,
        'is_required': question.is_required,
        'options': question.options,
        'created_at': question.created_at.isoformat(),
    }


def response_to_dict(response: SurveyResponse, include_answers: bool = False) -> dict:
    data = {
        'id': response.id,
        'survey_id': response.survey_id,
        'user_id': response.user_id,
        'submitted_at': response.submitted_at.isoformat() if response.submitted_at else None,
        'is_complete': response.is_complete,
        'created_at': response.created_at.isoformat(),
    }
    if include_answers:
        data['answers'] = [answer_to_dict(a) for a in response.answers.all()]
    return data


def answer_to_dict(answer: Answer) -> dict:
    return {
        'id': answer.id,
        'question_id': answer.question_id,
        'answer_text': answer.answer_text,
        'answer_data': answer.answer_data,
    }
