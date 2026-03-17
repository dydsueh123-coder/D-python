# TASS — 업무 자동화 설문 시스템

**T**ask **A**utomation **S**urvey **S**ystem

임직원의 반복 업무를 파악하고 자동화 우선순위를 도출하기 위한 사내 설문 시스템입니다.
AD(LDAP) 인증 기반으로 별도 계정 관리 없이 사용하며, 화면 녹화 기능으로 실제 업무 흐름을 캡처할 수 있습니다.

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| **AD 인증** | leemock.local Active Directory 계정으로 로그인 |
| **설문 응답** | 단답형·장문형·단일/복수선택·척도 질문 지원 |
| **화면 녹화** | Chrome 화면 공유 → WebM 녹화 → 서버 업로드 |
| **관리자 빌더** | 드래그 없이 버튼으로 질문 추가/순서변경/삭제 |
| **자동화 대시보드** | 척도 평균 × ln(응답자 수) 공식으로 우선순위 자동 산출 |
| **사용자 관리** | 관리자 권한 부여/해제 (스위치 토글) |

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| Backend | Flask 3.1, SQLAlchemy, Flask-Migrate, Flask-Login |
| Database | PostgreSQL 15 (pg8000 드라이버) |
| LDAP | ldap3 2.9.1 |
| Frontend | React 18 + TypeScript, Vite, Ant Design 5, Axios, Zustand |
| 배포 | Docker Compose (postgres + gunicorn + nginx) |

---

## 디렉터리 구조

```
automation-survey-system/
├── backend/
│   ├── app/
│   │   ├── auth/          # LDAP 인증, Flask-Login
│   │   ├── surveys/       # 설문 CRUD, 응답 처리
│   │   ├── recordings/    # 화면 녹화 업로드/서빙
│   │   ├── analytics/     # 통계, 우선순위 랭킹
│   │   └── admin/         # 사용자 관리
│   ├── migrations/        # Alembic DB 마이그레이션
│   ├── tests/             # pytest 테스트 (48개)
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── Dockerfile
│   └── wsgi.py
├── frontend/
│   ├── src/
│   │   ├── pages/         # 페이지 컴포넌트
│   │   ├── components/    # 공통/설문 컴포넌트
│   │   ├── api/           # Axios API 클라이언트
│   │   ├── hooks/         # useScreenRecorder 등
│   │   ├── stores/        # Zustand 상태
│   │   └── types/         # TypeScript 타입
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml
└── docs/
    └── HANDOFF-20260317.md
```

---

## 빠른 시작

### 방법 1: Docker Compose (권장)

#### 1. 환경 파일 준비

```bash
cd automation-survey-system
cp .env.example .env   # 없으면 아래 내용으로 직접 생성
```

`.env` 파일 내용:

```env
# Flask
SECRET_KEY=your-very-secret-key-change-this

# PostgreSQL (Docker 내부 컨테이너용)
POSTGRES_DB=tass_dev
POSTGRES_USER=tass_user
POSTGRES_PASSWORD=tass_password

# LDAP (사내 AD 정보)
LDAP_SERVER=ldap://ad1.leemock.local
LDAP_BASE_DN=DC=leemock,DC=local
LDAP_USER_SEARCH_BASE=OU=LeeMockUsers,DC=leemock,DC=local
LDAP_BIND_USER_DN=CN=서비스계정명,OU=전산팀,OU=LeeMockUsers,DC=leemock,DC=local
LDAP_PASSWORD=서비스계정_비밀번호

# 포트 (기본 80)
APP_PORT=80
```

#### 2. 빌드 및 기동

```bash
docker compose up -d --build
```

#### 3. DB 마이그레이션

```bash
# 컨테이너가 뜬 후 실행
docker compose exec backend flask db upgrade
```

#### 4. 접속

브라우저에서 `http://서버IP` 접속 → AD 계정으로 로그인

---

### 방법 2: 로컬 개발 환경

#### 사전 요구사항

- Python 3.12+
- Node.js 20+
- PostgreSQL 접근 가능 (172.16.2.110:5432 또는 로컬)

---

#### Backend 실행

```bash
# 1. 디렉터리 이동
cd automation-survey-system/backend

# 2. 가상환경 생성 및 활성화
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 3. 패키지 설치
pip install -r requirements-dev.txt

# 4. 환경 파일 설정
# .env 파일이 automation-survey-system/ 루트에 있어야 합니다
# (또는 backend/ 안에 복사)

# 5. DB 마이그레이션
flask db upgrade

# 6. 개발 서버 실행 (포트 5000)
set FLASK_APP=wsgi.py      # Windows
export FLASK_APP=wsgi.py   # Mac/Linux

flask run
# 또는
python wsgi.py
```

백엔드 확인:
```bash
curl http://localhost:5000/api/health
# 응답: {"status": "ok"}
```

---

#### Frontend 실행

```bash
# 1. 디렉터리 이동
cd automation-survey-system/frontend

# 2. 패키지 설치
npm install

# 3. 개발 서버 실행 (포트 5173)
npm run dev
```

브라우저에서 `http://localhost:5173` 접속

> **참고**: Vite 개발 서버는 `/api/` 요청을 자동으로 `localhost:5000`으로 프록시합니다.
> `vite.config.ts`에 프록시 설정이 없다면 아래를 추가하세요:
>
> ```ts
> // vite.config.ts
> export default defineConfig({
>   plugins: [react()],
>   server: {
>     proxy: {
>       '/api': 'http://localhost:5000',
>     },
>   },
> })
> ```

---

#### Frontend 프로덕션 빌드

```bash
cd automation-survey-system/frontend
npm run build
# dist/ 디렉터리에 정적 파일 생성됨
```

---

## DB 마이그레이션 관리

```bash
cd automation-survey-system/backend

# 마이그레이션 파일 생성 (모델 변경 후)
flask db migrate -m "변경 내용 설명"

# 마이그레이션 적용
flask db upgrade

# 한 단계 롤백
flask db downgrade

# 현재 적용 상태 확인
flask db current

# 마이그레이션 이력 조회
flask db history
```

---

## 테스트 실행

```bash
cd automation-survey-system/backend

# 가상환경 활성화 후
pip install -r requirements-dev.txt

# 전체 테스트 실행
python -m pytest tests/ -v

# 커버리지 포함
python -m pytest tests/ -v --cov=app --cov-report=term-missing

# 특정 모듈만
python -m pytest tests/test_surveys/ -v
python -m pytest tests/test_analytics/ -v
python -m pytest tests/test_recordings/ -v
```

예상 결과:
```
48 passed in 2.xx s
```

---

## API 주요 엔드포인트

### 인증
| 메서드 | URL | 설명 |
|--------|-----|------|
| POST | `/api/auth/login` | AD 로그인 |
| POST | `/api/auth/logout` | 로그아웃 |
| GET | `/api/auth/me` | 현재 사용자 정보 |

### 설문
| 메서드 | URL | 설명 | 권한 |
|--------|-----|------|------|
| GET | `/api/surveys/` | 설문 목록 | 로그인 |
| POST | `/api/surveys/` | 설문 생성 | 관리자 |
| GET | `/api/surveys/<id>` | 설문 상세 (질문 포함) | 로그인 |
| PUT | `/api/surveys/<id>` | 설문 수정 | 관리자 |
| DELETE | `/api/surveys/<id>` | 설문 삭제 | 관리자 |
| POST | `/api/surveys/<id>/activate` | 활성화 | 관리자 |
| POST | `/api/surveys/<id>/close` | 종료 | 관리자 |
| POST | `/api/surveys/<id>/questions` | 질문 추가 | 관리자 |
| PUT | `/api/surveys/<id>/questions/<qid>` | 질문 수정 | 관리자 |
| DELETE | `/api/surveys/<id>/questions/<qid>` | 질문 삭제 | 관리자 |
| PUT | `/api/surveys/<id>/questions/reorder` | 질문 순서 변경 | 관리자 |
| POST | `/api/surveys/<id>/responses` | 응답 제출 | 로그인 |
| GET | `/api/surveys/<id>/responses/mine` | 내 응답 조회 | 로그인 |
| GET | `/api/surveys/<id>/responses` | 전체 응답 목록 | 관리자 |

### 화면 녹화
| 메서드 | URL | 설명 | 권한 |
|--------|-----|------|------|
| POST | `/api/recordings/upload` | WebM 업로드 | 로그인 |
| GET | `/api/recordings/` | 녹화 목록 | 로그인 |
| GET | `/api/recordings/<id>/file` | 파일 스트리밍 | 본인/관리자 |
| DELETE | `/api/recordings/<id>` | 삭제 | 본인/관리자 |

### 분석 / 관리자
| 메서드 | URL | 설명 | 권한 |
|--------|-----|------|------|
| GET | `/api/analytics/dashboard` | 전체 통계 요약 | 관리자 |
| GET | `/api/analytics/priority` | 자동화 우선순위 랭킹 | 관리자 |
| GET | `/api/analytics/surveys/<id>` | 설문별 응답 통계 | 관리자 |
| GET | `/api/admin/users` | 사용자 목록 | 관리자 |
| PUT | `/api/admin/users/<id>/admin` | 관리자 권한 토글 | 관리자 |

---

## 로그인 후 사용 흐름

### 일반 직원

```
로그인 → 설문 목록 → [응답하기] 클릭
  → 화면 녹화 시작 (선택) → 업무 화면 캡처
  → 설문 질문에 응답 → 제출
  → 완료 화면에서 추가 녹화 업로드 가능
```

### 관리자

```
로그인 → 관리자 대시보드
  → [새 설문 만들기] → 제목/설명/기간 입력 → 생성
  → 질문 추가 (유형 선택 → 내용 입력 → 선택지 설정)
  → [활성화] → 직원들이 응답 시작
  → 응답 현황 확인 → [통계] → 질문별 분포 확인
  → 자동화 우선순위 랭킹으로 고효율 자동화 대상 선정
  → [설문 종료]
```

---

## 관리자 계정 지정

초기에는 관리자가 없습니다. DB에서 직접 지정합니다:

```bash
# psql 접속 후
UPDATE users SET is_admin = true WHERE username = '사용자ID';
```

이후부터는 관리자 대시보드 → 사용자 관리 → 스위치 토글로 GUI에서 변경 가능합니다.

---

## 운영 시 주의사항

### 파일 업로드 (화면 녹화)

- 녹화 파일은 `uploads/recordings/` 디렉터리에 저장됩니다
- Docker 사용 시 `uploads_data` 볼륨으로 영구 보존됩니다
- 최대 크기: **500MB/파일**
- 파일명은 UUID로 자동 생성 (경로 조작 불가)
- 주기적으로 오래된 파일 정리 권장

### LDAP 연결

- `LDAP_BIND_USER_DN`: 사용자 검색용 서비스 계정 DN
- AD에서 서비스 계정 비밀번호 만료 설정을 "만료 없음"으로 해두면 운영 편의성이 높아집니다
- LDAP 장애 시 로그인 불가 → 비상 접근용 DB 계정 별도 운용 고려

### 세션 만료

- 세션 TTL: **8시간** (로그인 후 8시간 뒤 자동 만료)
- `app/config.py`의 `PERMANENT_SESSION_LIFETIME`에서 조정 가능

---

## 트러블슈팅

### DB 연결 실패

```bash
# PostgreSQL 접속 확인
psql -h 172.16.2.110 -U postgres -d tass_dev

# pg8000 특이사항: 비밀번호에 @ 포함 시 %40으로 인코딩
# 예: DATABASE_URL=postgresql+pg8000://user:%40password@host/db
```

### LDAP 인증 실패

```bash
# AD 서버 연결 확인
python -c "
from ldap3 import Server, Connection
s = Server('ldap://ad1.leemock.local')
c = Connection(s, 'CN=계정,DC=leemock,DC=local', '비밀번호', auto_bind=True)
print('LDAP OK:', c.bound)
"
```

### 화면 녹화 안 됨

- Chrome 브라우저 필수 (Firefox/Safari 미지원)
- `https://` 또는 `localhost`에서만 `getDisplayMedia` 동작
- 사내 HTTP 서버인 경우: Chrome에서 `chrome://flags/#unsafely-treat-insecure-origin-as-secure` 설정

### 업로드 디렉터리 권한 오류

```bash
# 컨테이너 내부
docker compose exec backend mkdir -p /app/uploads/recordings
docker compose exec backend chmod 755 /app/uploads/recordings
```

---

## 개발 환경 정보

- **LDAP DC**: `ad1.leemock.local` (`dc.leemock.local` DNS 미등록)
- **DB 드라이버**: `pg8000` (psycopg2 사용 불가 — Windows CP949 환경 UnicodeDecodeError)
- **DB 연결**: `postgresql+pg8000://` URL 스킴 사용
- **테스트 DB**: SQLite in-memory (PostgreSQL 불필요)
