# Project Zomboid Analytics

Project Zomboid 인게임 데이터를 Lua 모드로 추출하고, Python ETL 파이프라인으로
정형화한 뒤 데이터 품질 CI와 대시보드까지 한 흐름에 묶은 포트폴리오 프로젝트.

## 아키텍처

```
+--------------------+    CSV     +--------------------+   pytest +    +-------------------+
| PZ Lua mod         | ---------> | etl/ (extract /    |   GitHub | -->| dashboard/        |
| (DataDumper)       |  data/raw/ |  transform / load) |   Actions|    | (Streamlit)       |
+--------------------+            +---------+----------+          |    +-------------------+
                                            |                     |
                                            v                     |
                                   SQLite warehouse <-------------+
                                   (data/processed/zomboid.db)
                                            |
                                            v
                                   analysis/ + models/
                                   (PuLP / PyTorch 추후 작업)
```

## Why this repo (원라이너)

> "10시간 차 좌보이드 뉴비가 피지컬 대신 ETL 파이프라인과 데이터 품질 CI를
> 들고 와서 게임을 분석으로 풀어보겠다는 시도."

데이터 엔지니어 포트폴리오로서의 핵심은 **`etl/`** + **`db/schema.sql`** +
**`tests/test_data_quality.py`** + **`.github/workflows/data-quality.yml`** 콤보.
샘플 픽스처가 들어 있어서 **게임 없이도 CI가 초록색으로 통과**한다.

## 빠른 시작

```bash
pip install -r requirements.txt
make etl-fixtures        # tests/fixtures 을 /tmp/zomboid.db 로 적재
make test                # pytest 데이터 품질 게이트
make lint
make dashboard           # Streamlit UI 띄우기
```

게임 세션 진행 중 실시간 스트리밍:

```bash
python -m etl.watchdog_runner --input ~/Zomboid/Lua --db data/processed/zomboid.db
```

## 디렉토리 구조

```
project-zomboid-analytics/
├── lua-mods/DataDumper/       # 인게임 데이터 추출 모드 (PZ Build 41.78)
├── etl/                       # Python ETL (extract / transform / load)
│   ├── extract.py             #   raw CSV discovery + load
│   ├── transform.py           #   schema-enforced type coercion
│   ├── load.py                #   SQLAlchemy → SQLite
│   ├── pipeline.py            #   CLI entrypoint (python -m etl)
│   └── watchdog_runner.py     #   live ingestion
├── db/schema.sql              # 단일 진실 원본 (DDL)
├── tests/                     # pytest 기반 데이터 품질 게이트
│   ├── test_data_quality.py
│   ├── test_etl.py
│   └── fixtures/              # CI 통과용 합성 CSV
├── dashboard/app.py           # Streamlit 생존 대시보드
├── bridge/                    # Phase 3 Claude API 브릿지
├── data/
│   ├── raw/                   # gitignore (게임 세션 출력)
│   ├── processed/             # gitignore (SQLite warehouse)
│   └── schemas/               # CSV 컴럼 정의 (사람용 문서)
└── .github/workflows/         # data-quality.yml, lint.yml
```

## 데이터 파이프라인 단계

| 단계 | 책임 | 도구 |
|------|------|------|
| Extract | DataDumper Lua mod이 `~/Zomboid/Lua/`에 CSV 덤프 | Lua `getFileWriter` |
| Transform | 컴럼 누락 거부 + dtype 강제 + 음수 시간 드롭 | pandas + `etl/transform.py` |
| Load | 멱등 DDL 후 append | SQLAlchemy + SQLite |
| Validate | 좌표 범위 / 정규화 범위 / PK 중복 / 단조성 | pytest in CI |
| Visualize | 세션 선택형 시계열·히트맵 | Streamlit + Plotly |

## 3단계 로드맵

| Phase | 아이디어 | Claude (Lua/DE) | Antigravity (Python/ML) | 상태 |
|-------|---------|------------------|-------------------------|------|
| 1 | Nutrition Optimizer | DataDumper Lua 모드 + ETL/DB 완 | PuLP ILP로 최적 식단 | 🚀 진행 중 |
| 2 | Zombie Heatmap | 좌비 좌표 샘플링 완 | KDE → 시계열 GRU | 📋 예정 |
| 3 | LLM Radio Mod | 게임 상태 JSON 직렬화 | bridge/radio_server.py 완 | 📋 예정 |

## 역할 분담

- **Crong (Tech Lead)**: 기획, DE 방향성, 최종 QA
- **Claude**: Lua 모딩 + Python ETL/DB 인프라
- **Antigravity**: 분석·모델링 (analysis/, models/, 식단 ILP)

세부 합의는 `AGENTS.md` 참고.

## 개발 환경

- Project Zomboid Build 41.78 (Steam, stable)
- 모드 경로: `%ProgramFiles(x86)%/Steam/steamapps/common/ProjectZomboid/mods/`
- Lua 출력 경로: `%UserProfile%/Zomboid/Lua/`
- Python 3.11+, see `requirements.txt`
