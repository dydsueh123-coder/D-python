"""
초기 설문 시드 스크립트
plan.md Phase 3.2 기준 기본 설문 문항 탑재

실행: python seed_survey.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import db
from app.surveys.models import Survey, Question

SURVEY_TITLE = "업무 자동화 수요 파악 설문"
SURVEY_DESCRIPTION = (
    "직원 여러분의 반복/단순 업무를 파악하여 자동화 우선순위를 도출하기 위한 설문입니다.\n"
    "각 문항에 솔직하게 답변해 주시면 보다 효율적인 업무 환경을 만드는 데 큰 도움이 됩니다.\n"
    "응답 시간: 약 10~15분 / 화면 녹화로 실제 업무 과정을 공유해 주시면 더욱 정확한 분석이 가능합니다."
)

QUESTIONS = [
    # ── 카테고리 A: 업무 기본 정보 ───────────────────────────────
    {
        "order_num": 1,
        "question_type": "textarea",
        "question_text": "[A1] 현재 수행하고 있는 주요 업무를 간단히 설명해 주세요.",
        "is_required": True,
        "options": None,
    },
    {
        "order_num": 2,
        "question_type": "checkbox",
        "question_text": "[A2] 해당 업무의 분류를 선택해 주세요. (복수 선택 가능)",
        "is_required": True,
        "options": [
            "서류 작성/편집",
            "데이터 입력/관리",
            "이메일/커뮤니케이션",
            "일정/기한 관리",
            "시스템 조회/검색",
            "파일 정리/분류",
            "보고서/통계 작성",
            "번역/언어 관련",
            "고객 응대",
            "기타",
        ],
    },
    {
        "order_num": 3,
        "question_type": "checkbox",
        "question_text": "[A3] 해당 업무에서 주로 사용하는 도구/시스템을 선택해 주세요. (복수 선택 가능)",
        "is_required": True,
        "options": [
            "LIPMS",
            "Microsoft Word",
            "Microsoft Excel",
            "Microsoft PowerPoint",
            "Outlook/Exchange",
            "특허로 (KIPRIS)",
            "WIPO PCT 시스템",
            "웹 브라우저",
            "파일 탐색기",
            "기타 (직접 입력)",
        ],
    },
    # ── 카테고리 B: 반복성 및 빈도 ───────────────────────────────
    {
        "order_num": 4,
        "question_type": "radio",
        "question_text": "[B1] 이 업무를 얼마나 자주 수행하시나요?",
        "is_required": True,
        "options": [
            "하루 여러 번",
            "하루 1회",
            "주 2~3회",
            "주 1회",
            "월 1~2회",
            "비정기적",
        ],
    },
    {
        "order_num": 5,
        "question_type": "radio",
        "question_text": "[B2] 한 번 수행 시 평균 소요 시간은 얼마인가요?",
        "is_required": True,
        "options": [
            "5분 미만",
            "5~15분",
            "15~30분",
            "30분~1시간",
            "1시간~2시간",
            "2시간 이상",
        ],
    },
    {
        "order_num": 6,
        "question_type": "scale",
        "question_text": "[B3] 이 업무의 절차가 매번 거의 동일한가요? (1: 매번 다름 ~ 5: 항상 동일한 절차)",
        "is_required": True,
        "options": None,
    },
    {
        "order_num": 7,
        "question_type": "scale",
        "question_text": "[B4] 이 업무를 수행할 때 판단이나 의사결정이 필요한 정도는? (1: 판단 거의 불필요 ~ 5: 매번 복잡한 판단 필요)",
        "is_required": True,
        "options": None,
    },
    # ── 카테고리 C: 자동화 가능성 평가 ───────────────────────────
    {
        "order_num": 8,
        "question_type": "textarea",
        "question_text": "[C1] 이 업무에서 가장 시간이 오래 걸리는 단계는 무엇인가요?",
        "is_required": True,
        "options": None,
    },
    {
        "order_num": 9,
        "question_type": "textarea",
        "question_text": "[C2] 이 업무 중 '기계적으로 반복'한다고 느끼는 부분이 있나요?\n(예: 매번 같은 양식에 같은 위치에 데이터를 복사-붙여넣기 한다)",
        "is_required": False,
        "options": None,
    },
    {
        "order_num": 10,
        "question_type": "textarea",
        "question_text": "[C3] 이 업무를 자동화할 수 있다면, 어떤 부분이 자동화되길 원하시나요?",
        "is_required": True,
        "options": None,
    },
    {
        "order_num": 11,
        "question_type": "radio",
        "question_text": "[C4] 현재 이 업무에서 실수가 발생하는 빈도는?",
        "is_required": True,
        "options": [
            "거의 없음",
            "가끔 (월 1~2회)",
            "종종 (주 1~2회)",
            "자주 (거의 매일)",
        ],
    },
    {
        "order_num": 12,
        "question_type": "radio",
        "question_text": "[C5] 실수 발생 시 영향도는 어느 정도인가요?",
        "is_required": True,
        "options": [
            "경미 (즉시 수정 가능)",
            "보통 (수정에 추가 시간 소요)",
            "심각 (고객/기한에 영향)",
            "치명적 (법적/재무적 문제 가능)",
        ],
    },
    # ── 카테고리 D: 업무 환경 및 데이터 ──────────────────────────
    {
        "order_num": 13,
        "question_type": "checkbox",
        "question_text": "[D1] 이 업무에서 다루는 데이터의 형태는? (복수 선택 가능)",
        "is_required": True,
        "options": [
            "텍스트/문서",
            "스프레드시트/표",
            "이메일",
            "PDF",
            "이미지/스캔본",
            "웹 데이터",
            "데이터베이스",
            "기타",
        ],
    },
    {
        "order_num": 14,
        "question_type": "radio",
        "question_text": "[D2] 여러 시스템 간 데이터를 수동으로 옮기는 작업이 있나요?",
        "is_required": True,
        "options": [
            "없음",
            "가끔 있음",
            "자주 있음",
            "거의 항상",
        ],
    },
    {
        "order_num": 15,
        "question_type": "textarea",
        "question_text": "[D3] 데이터를 옮기는 경우, 어디에서 어디로 옮기나요?\n(예: LIPMS에서 Excel로 기한 목록을 복사)",
        "is_required": False,
        "options": None,
    },
    # ── 카테고리 E: 추가 의견 ────────────────────────────────────
    {
        "order_num": 16,
        "question_type": "textarea",
        "question_text": "[E1] 자동화되면 가장 도움이 될 것 같은 업무 TOP 3를 자유롭게 적어주세요.",
        "is_required": True,
        "options": None,
    },
    {
        "order_num": 17,
        "question_type": "textarea",
        "question_text": "[E2] 업무 중 불편하거나 비효율적이라고 느끼는 점이 있으면 자유롭게 적어주세요.",
        "is_required": False,
        "options": None,
    },
    {
        "order_num": 18,
        "question_type": "radio",
        "question_text": "[E3] 화면 녹화를 통해 해당 업무 수행 과정을 공유해 주실 수 있나요?",
        "is_required": True,
        "options": [
            "예, 지금 녹화하겠습니다",
            "예, 나중에 녹화하겠습니다",
            "아니요, 녹화는 어렵습니다",
        ],
    },
    {
        "order_num": 19,
        "question_type": "textarea",
        "question_text": "[E4] 기타 의견이나 요청사항이 있으시면 자유롭게 작성해 주세요.",
        "is_required": False,
        "options": None,
    },
]


def seed():
    app = create_app('development')
    with app.app_context():
        # 중복 실행 방지
        existing = Survey.query.filter_by(title=SURVEY_TITLE).first()
        if existing:
            print(f"[SKIP] 이미 존재하는 설문: '{SURVEY_TITLE}' (id={existing.id})")
            print("       재생성하려면 DB에서 해당 설문을 삭제 후 다시 실행하세요.")
            return

        survey = Survey(
            title=SURVEY_TITLE,
            description=SURVEY_DESCRIPTION,
            status='active',  # 즉시 응답 가능하도록 활성화
        )
        db.session.add(survey)
        db.session.flush()  # id 확보

        for q_data in QUESTIONS:
            question = Question(
                survey_id=survey.id,
                order_num=q_data["order_num"],
                question_type=q_data["question_type"],
                question_text=q_data["question_text"],
                is_required=q_data["is_required"],
                options=q_data["options"],
            )
            db.session.add(question)

        db.session.commit()
        print(f"[OK] 설문 생성 완료: '{SURVEY_TITLE}' (id={survey.id})")
        print(f"     질문 수: {len(QUESTIONS)}개 / 상태: active")
        print(f"     브라우저에서 http://localhost:5173/surveys 접속 시 바로 확인 가능")


if __name__ == '__main__':
    seed()
