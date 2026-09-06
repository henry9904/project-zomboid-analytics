# AGENTS.md — Project Zomboid Analytics

## 프로젝트 역할 분담

| 에이전트 | 담당 영역 | 작업 디렉토리 |
|---------|---------|-------------|
| **Claude** | Lua 모딩, 데이터 엔지니어링 (ETL/DB/CI) | `lua-mods/`, `etl/`, `db/`, `tests/`, `dashboard/`, `.github/workflows/` |
| **Antigravity** | Python 분석, EDA, PyTorch 모델링 | `analysis/`, `models/`, `data/processed/` |
| **Crong (Tech Lead)** | 기획, 방향 설정, 최종 의사결정 | 전체 |

알림: 데이터 엔지니어링은 Claude가 소유. Antigravity는 이미 적재된
warehouse(`data/processed/zomboid.db`)에서 읽어서 분석만 돌린다.
ETL/CI/대시보드는 건드리지 않는다.

---

## Claude — 데이터 엔지니어링 가이드 (DE)

### 아키텍처 원칙

1. **스키마는 `db/schema.sql`이 단일 진실 원본.** Python `transform.SCHEMAS`와
   항상 일치시킬 것.
2. **스키마 변경 흐름**: `data/schemas/*.md` 문서 변경 → `db/schema.sql` 반영
   → `etl/transform.py` SCHEMAS 업데이트 → `tests/fixtures/*.csv` 업데이트
   → 필요시 새 품질 테스트.
3. **CI는 반드시 직접 돌려볼 것.** 픽스처 CSV로 전체 ETL이 돌고
   `pytest`가 그린이어야 한다.
4. **멱등성**: `etl.load.init_db`는 `CREATE TABLE IF NOT EXISTS`만 쓴다. ETL을
   여러 번 돌려도 안전해야 함.
5. **`data/raw/`, `data/processed/`는 gitignore.** 세션 데이터는 컬밋 금지.

### ETL CLI

```bash
python -m etl --input data/raw --db data/processed/zomboid.db --verbose
python -m etl.watchdog_runner --input ~/Zomboid/Lua --db data/processed/zomboid.db
```

### 데이터 품질 게이트 (CI)

`tests/test_data_quality.py` 는 아래 불변속성을 검증:

- 좌표가 맵 범위 0–15000 내
- `hunger`, `thirst`, `fatigue`, `stress`, `panic`, `boredom` 이 [0, 1]
- `weight` 가 [30, 200] kg
- `(session_id, world_age_hours)` PK 중복 없음
- 세션 내 `world_age_hours` 단조 증가

새 품질 규칙 추가할 때는 `test_data_quality.py`에 함수 추가 + 필요하면
픽스처 업데이트.

### Lua 모드 소스 구조

```
lua-mods/DataDumper/
├── mod.info
└── media/lua/client/
    ├── DataDumper_Init.lua          # 파일 writer + 헤더 초기화
    ├── PlayerStatsLogger.lua        # 2 게임시간 틱
    ├── ZombieLogger.lua             # 6 게임시간 틱, 50셀 반경
    ├── NoiseLogger.lua              # Events.OnPlayerAttackFinished
    └── InventoryLogger.lua          # 2 게임시간 틱, 식품 집계
```

Lua 출력 경로: `%UserProfile%/Zomboid/Lua/`. 파일명 규칙은
`<dataset>_session_<session_id>.csv` (ETL의 `extract.discover` 와 일치).

### 주요 Lua API

```lua
local player = getSpecificPlayer(0)
local stats  = player:getStats()           -- hunger/thirst/fatigue/stress/panic/boredom
local nutri  = player:getNutrition()       -- calories/weight/carbs/proteins/lipids
local gt     = getGameTime()               -- worldAgeHours / timeOfDay / nightsSurvived
local cell   = getCell()
local zlist  = cell:getZombieList()        -- IsoZombie list
local inv    = player:getInventory():getItems()
```

### 이벤트 훅

| 이벤트 | 시점 |
|--------|------|
| `Events.OnGameStart` | 게임 로딩 완료 시 — 헤더 초기화 |
| `Events.OnTickEvenHours` | 2 게임시간마다 (주기 로깅) |
| `Events.OnPlayerAttackFinished` | 공격 완료 — 소음 이벤트 |
| `Events.OnSave` | 저장 시점 — flush 안전 |

---

## Antigravity — Python/ML 가이드

### 입력 데이터 위치

클롤게 엄격히 말하면 **`data/processed/zomboid.db` (SQLite warehouse)** 가
공식 입력이다. 원본 CSV를 직접 읽지 말 것.

```python
import sqlite3, pandas as pd
conn = sqlite3.connect("data/processed/zomboid.db")
player = pd.read_sql("SELECT * FROM player_stats", conn)
zombies = pd.read_sql("SELECT * FROM zombie_sightings", conn)
inventory = pd.read_sql("SELECT * FROM inventory_snapshots", conn)
```

### 스키마 문서

새 컴럼이 필요하면 `data/schemas/*.md`를 먼저 읽고, Claude에게
스키마 확장을 요청할 것. **직접 ETL을 수정하지 말 것.**

### Phase 1 — Nutrition Optimizer 작업 지침

**목표**: 보유 식량 조합으로 체중 유지 + 생존 일수 극대화 식단 스케줄

**입력**: `inventory_snapshots` + `player_stats`

**알고리즘 후보** (Claude 추천 순):
1. **Greedy Knapsack** (구현 빠름, 기준선)
2. **PuLP ILP** (영양 제약 + 칼로리 최적화에 적합)
3. **Simulated Annealing** (며칠치 식단 스케줄 최적화 시)

**결과 저장**: `nutrition_plan` 테이블에 (session_id, day_idx, item_type, servings, total_calories)

### Phase 2 — Zombie Heatmap 작업 지침

**목표**: 소음 이벤트 발생 후 N 게임시간 뒤 좌비 밀집 위치 예측 히트맵

**입력**: `zombie_sightings` + `noise_events`

**모델 방향**:
- 기준선: 커널 밀도 추정(KDE) 히트맵
- 개선: `mosquito-trajectory-prediction` 레포의 Kalman + GRU 구조 재활용
  (body-frame 정규화 동일 적용)

### Phase 3 — LLM Radio Bridge

**아키텍처**:
```
PZ 게임 (Lua) → game_state.json 파일 write
  → bridge/radio_server.py (파일 감시 + Claude API 호출)
  → response.json 파일 write
  → PZ 게임 (Lua) → UI 텍스트 표시
```

---

## 공통 규칙

1. **브랜치**: 현재 세션 작업 브랜치는 `claude/admiring-goldberg-KKOgu`.
   다음 세션은 하니스 지정 브랜치를 따른다.
2. **커밋 메시지**: 작성자 구분을 위해 `[claude]` 또는 `[antigravity]`
   접두사 권장.
3. **data/raw/, data/processed/**: gitignore. 게임 세션 데이터는 컬밋 금지.
4. **스키마 먼저**: 새 데이터 형식 추가 시 `data/schemas/`에 정의 문서 먼저,
   `db/schema.sql`과 `etl/transform.py` SCHEMAS 동기화 필수.
5. **mod.info require**: Lua 모드는 의존성 없이 바닐라만으로 동작.

---

## AI Mistakes Log

형식: `날짜 | 에이전트 | 실수 내용 | 영향 | 수정 방법 | 교훈`

| 날짜 | 에이전트 | 실수 | 영향 | 수정 | 교훈 |
|------|---------|------|------|------|------|
| (기록 없음) | — | — | — | — | — |

> 실수 발생 시 위 테이블에 추가. 같은 실수 반복 방지가 목적.

---

## 프로젝트 상태 체크리스트

### 데이터 엔지니어링 (Claude)
- [x] `db/schema.sql` 단일 진실 원본 DDL
- [x] `etl/` extract / transform / load / pipeline / watchdog_runner
- [x] `tests/` 데이터 품질 게이트 + ETL 단위 테스트 + 픽스처
- [x] `.github/workflows/data-quality.yml`, `lint.yml`
- [x] `dashboard/app.py` Streamlit

### Phase 1 — Nutrition Optimizer
- [x] DataDumper Lua 모드 (PlayerStatsLogger, InventoryLogger)
- [x] `player_stats`, `inventory_snapshot` 스키마 문서
- [ ] PuLP ILP 구현 (Antigravity)
- [ ] `nutrition_plan` 테이블 적재

### Phase 2 — Zombie Heatmap
- [x] DataDumper Lua 모드 (ZombieLogger, NoiseLogger)
- [x] `zombie_log`, `noise_events` 스키마 문서
- [ ] KDE 기준선 (Antigravity)
- [ ] GRU 시계열 모델 (Antigravity)

### Phase 3 — LLM Radio Mod
- [x] `bridge/radio_server.py` watchdog + Claude API
- [ ] RadioBridge Lua mod 직렬화
- [ ] 게임 내 UI 테스트
