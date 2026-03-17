"""응답 통계 및 자동화 우선순위 점수 산출"""
from collections import Counter
from app.extensions import db
from app.surveys.models import Survey, Question, SurveyResponse, Answer
from app.auth.models import User
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:

    # ── 전체 대시보드 요약 ────────────────────────────────

    @staticmethod
    def get_dashboard_stats() -> dict:
        return {
            'total_surveys': Survey.query.count(),
            'active_surveys': Survey.query.filter_by(status='active').count(),
            'draft_surveys': Survey.query.filter_by(status='draft').count(),
            'closed_surveys': Survey.query.filter_by(status='closed').count(),
            'total_responses': SurveyResponse.query.filter_by(is_complete=True).count(),
            'total_users': User.query.count(),
        }

    # ── 자동화 우선순위 목록 ──────────────────────────────

    @classmethod
    def get_priority_ranking(cls) -> list:
        """
        모든 설문의 자동화 우선순위 점수를 산출하여 내림차순 반환.
        점수 = scale 질문 평균 × ln(응답자 수 + 1)
        — 응답자가 많을수록, 자동화 필요성이 높을수록 우선순위↑
        """
        import math
        surveys = Survey.query.filter(Survey.status.in_(['active', 'closed'])).all()
        ranking = []
        for survey in surveys:
            stats = cls._survey_stats(survey)
            score = stats['avg_scale_score'] * math.log1p(stats['total_responses'])
            ranking.append({
                'survey_id': survey.id,
                'survey_title': survey.title,
                'status': survey.status,
                'total_responses': stats['total_responses'],
                'avg_scale_score': round(stats['avg_scale_score'], 2),
                'automation_score': round(score, 2),
            })
        ranking.sort(key=lambda x: x['automation_score'], reverse=True)
        for i, item in enumerate(ranking):
            item['priority_rank'] = i + 1
        return ranking

    # ── 설문별 상세 통계 ──────────────────────────────────

    @classmethod
    def get_survey_analytics(cls, survey_id: int) -> dict | None:
        survey = Survey.query.get(survey_id)
        if not survey:
            return None
        stats = cls._survey_stats(survey)
        questions = survey.questions.order_by(Question.order_num).all()
        return {
            'survey_id': survey.id,
            'survey_title': survey.title,
            'status': survey.status,
            **stats,
            'questions': [cls._question_stats(q, stats['total_responses']) for q in questions],
        }

    # ── 내부 헬퍼 ─────────────────────────────────────────

    @staticmethod
    def _survey_stats(survey: Survey) -> dict:
        """설문 응답 수 + scale 문항 평균 점수 반환"""
        total = SurveyResponse.query.filter_by(
            survey_id=survey.id, is_complete=True
        ).count()

        # scale 질문 답변 평균
        scale_q_ids = [
            q.id for q in Question.query.filter_by(
                survey_id=survey.id, question_type='scale'
            ).all()
        ]
        avg_scale = 0.0
        if scale_q_ids and total > 0:
            rows = db.session.query(Answer.answer_data).filter(
                Answer.question_id.in_(scale_q_ids)
            ).all()
            # answer_data에 숫자(int/float) 저장됨
            values = []
            for (data,) in rows:
                try:
                    values.append(float(data))
                except (TypeError, ValueError):
                    pass
            if values:
                avg_scale = sum(values) / len(values)

        return {
            'total_responses': total,
            'avg_scale_score': avg_scale,
        }

    @staticmethod
    def _question_stats(question: Question, total_responses: int) -> dict:
        """질문별 집계: scale→평균, radio/checkbox→선택지별 카운트, text→응답 수"""
        base = {
            'question_id': question.id,
            'question_text': question.question_text,
            'question_type': question.question_type,
            'response_count': 0,
            'stats': {},
        }

        answers = Answer.query.filter_by(question_id=question.id).all()
        base['response_count'] = len(answers)

        if question.question_type == 'scale':
            values = []
            for a in answers:
                try:
                    values.append(float(a.answer_data))
                except (TypeError, ValueError):
                    pass
            base['stats'] = {
                'avg': round(sum(values) / len(values), 2) if values else 0,
                'min': min(values) if values else 0,
                'max': max(values) if values else 0,
                'distribution': dict(Counter(int(v) for v in values)),
            }

        elif question.question_type in ('radio', 'select'):
            counts = Counter(a.answer_data for a in answers if a.answer_data)
            base['stats'] = {'choices': dict(counts)}

        elif question.question_type == 'checkbox':
            counts: Counter = Counter()
            for a in answers:
                if isinstance(a.answer_data, list):
                    counts.update(a.answer_data)
            base['stats'] = {'choices': dict(counts)}

        else:
            # text / textarea: 응답 수만 표시
            base['stats'] = {'answered': len(answers)}

        # 응답률
        base['response_rate'] = (
            round(len(answers) / total_responses * 100, 1)
            if total_responses > 0 else 0
        )
        return base
