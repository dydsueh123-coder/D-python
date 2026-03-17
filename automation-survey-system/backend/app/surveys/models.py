from datetime import datetime
from app.extensions import db


class Survey(db.Model):
    """설문지"""
    __tablename__ = 'surveys'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft', nullable=False)  # draft, active, closed
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    questions = db.relationship('Question', backref='survey', lazy='dynamic', cascade='all, delete-orphan')
    responses = db.relationship('SurveyResponse', backref='survey', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Survey {self.id}: {self.title}>'


class Question(db.Model):
    """설문 질문"""
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    order_num = db.Column(db.Integer, nullable=False, default=0)
    question_type = db.Column(db.String(20), nullable=False)
    # 타입: text, textarea, radio, checkbox, scale, file
    question_text = db.Column(db.Text, nullable=False)
    is_required = db.Column(db.Boolean, default=True, nullable=False)
    options = db.Column(db.JSON)  # radio/checkbox 선택지
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    answers = db.relationship('Answer', backref='question', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Question {self.id}: {self.question_text[:30]}>'


class SurveyResponse(db.Model):
    """설문 응답 (응답자 단위)"""
    __tablename__ = 'survey_responses'

    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    submitted_at = db.Column(db.DateTime)
    is_complete = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    answers = db.relationship('Answer', backref='response', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<SurveyResponse {self.id}: survey={self.survey_id} user={self.user_id}>'


class Answer(db.Model):
    """개별 질문 응답"""
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey('survey_responses.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answer_text = db.Column(db.Text)
    answer_data = db.Column(db.JSON)  # 복수 선택, 점수 등
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Answer {self.id}: question={self.question_id}>'
