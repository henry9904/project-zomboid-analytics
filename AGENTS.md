# AGENTS.md — Project Zomboid Analytics

## 프로젝트 역할 분담

| 에이전트 | 담당 영역 | 작업 디렉토리 |
|---------|---------|-------------|
| **Claude** | Lua 모딩, 인게임 데이터 추출, 게임 API 분석 | `lua-mods/` |
| **Antigravity** | Python 데이터 전처리, EDA, PyTorch 모델링 | `data/processed/`, `analysis/`, `models/` |
| **Crong (Tech Lead)** | 기획, 방향 설정, 최종 의사결정 | 전체 |

---

## Claude — Lua 모딩 가이드

### 기본 모드 구조
PZ 모드는 반드시 아래 디렉토리 구조를 따름:
```
ModName/
├── mod.info          # 모드 메타데이터 (필수)
└── media/
    └── lua/
        ├── client/   # 클라이언트 사이드 (싱글플레이 포함)
        └── server/   # 서버 사이드 (멀티플레이 전용)
```

### 핵심 Lua API 레퍼런스

```lua
-- 플레이어 기본 정보
local player = getSpecificPlayer(0)          -- 로컬 플레이어
local x, y, z = player:getX(), player:getY(), player:getZ()

-- 스탯 (Stats 객체)
local stats = player:getStats()
local hunger  = stats:getHunger()            -- 0.0~1.0 (1.0 = 최대 허기)
local thirst  = stats:getThirst()
local fatigue = stats:getFatigue()
local stress  = stats:getStress()
local panic   = stats:getPanic()
local boredom = stats:getBoredom()

-- 영양 (Nutrition 모듈 — Build 41+)
local nutrition = player:getNutrition()
local calories  = nutrition:getCalories()
local weight    = nutrition:getWeight()
local carbs     = nutrition:getCarbohydrates()
local protein   = nutrition:getProteins()
local fat       = nutrition:getLipids()

-- 게임 시간
local gameTime  = getGameTime()
local worldAge  = gameTime:getWorldAgeHours()  -- 누적 게임 시간(시)
local hour      = gameTime:getTimeOfDay()       -- 현재 시각(시)
local day       = gameTime:getNightsSurvived()  -- 생존 일수

-- 날씨
local climate   = getClimateManager()
local temp      = climate:getTemperature()
local isRaining = climate:getRaining() > 0
local windSpeed = climate:getWindSpeed()

-- 좀비 목록 (현재 로드된 셀 내)
local zombieList = getCell():getZombieList()
for i = 0, zombieList:size() - 1 do
    local z = zombieList:get(i)
    local zx, zy = z:getX(), z:getY()
    -- z:getState() 로 상태(wandering/chasing 등) 확인 가능
end

-- 인벤토리
local inv = player:getInventory()
local items = inv:getItems()
for i = 0, items:size() - 1 do
    local item = items:get(i)
    local itemType = item:getType()   -- 예: "Base.Bread"
    local count = 1  -- Stack이면 item:getCount()
end
```

### 파일 출력 패턴
```lua
-- PZ에서 외부 파일 쓰기 (getGameTime 타임스탬프 활용)
local function writeCSVLine(filename, line)
    local writer = getFileWriter(filename, true, false)  -- append mode
    writer:write(line .. "\n")
    writer:close()
end
-- 출력 위치: %UserProfile%/Zomboid/Lua/<filename>
```

### 이벤트 훅 목록 (자주 쓰는 것)
| 이벤트 | 시점 |
|--------|------|
| `Events.OnTickEvenHours` | 2게임시간마다 (성능 절약용 주기 로깅) |
| `Events.OnZombieDead` | 좀비 사망 시 |
| `Events.OnNoise` | 소음 이벤트 발생 시 |
| `Events.OnPlayerDeath` | 플레이어 사망 시 |
| `Events.OnSave` | 게임 저장 시 (안전한 flush 타이밍) |

### 성능 주의사항
- `getCell():getZombieList()` 는 매 틱 호출 금지 — `OnTickEvenHours` 또는 5분 간격으로 샘플링
- 파일 write는 `OnSave` 또는 일정 버퍼(100줄) 이후 flush
- 모드 활성화 여부: `mod.info`의 `require=` 필드로 바닐라만 지정하면 어떤 모드셋에서도 동작

---

## Antigravity — Python/ML 가이드

### 입력 데이터 위치
```
data/raw/          # Lua 모드가 생성한 원본 CSV/JSON (gitignore됨)
data/processed/    # 전처리 완료 DataFrame (.parquet 권장)
data/schemas/      # 각 파일의 컬럼 정의 (반드시 먼저 읽을 것)
```

### 스키마 파일 우선 확인
작업 시작 전 반드시 `data/schemas/` 내 `.md` 파일을 읽을 것.
스키마 없이 raw CSV를 직접 파싱하면 컬럼 오해 발생 가능.

### Phase 1 — Nutrition Optimizer 작업 지침

**목표**: 보유 식량 조합으로 체중 유지 + 생존 일수 극대화 식단 스케줄 생성

**데이터 파일**: `data/raw/nutrition_session_*.csv`

**알고리즘 후보** (Claude 추천 순):
1. **Greedy Knapsack** (구현 빠름, 기준선)
2. **Integer Linear Programming** (scipy.optimize / PuLP) — 영양 제약 + 칼로리 최적화에 적합
3. **Simulated Annealing** (며칠치 식단 스케줄 최적화 시)

**금지 사항**:
- 과도한 feature engineering 전에 단순 greedy 기준선부터 잡을 것
- 바닐라 식품 DB 외 모드 아이템을 가정한 하드코딩 금지

### Phase 2 — Zombie Heatmap 작업 지침

**목표**: 소음 이벤트 발생 후 N 게임시간 뒤 좀비 밀집 위치 예측 히트맵

**데이터 파일**: `data/raw/zombie_log_*.csv`

**모델 방향**:
- 기준선: 커널 밀도 추정(KDE) 히트맵
- 개선: `mosquito-trajectory-prediction` 레포의 Kalman + GRU 구조 재활용 (body-frame 정규화 동일하게 적용)
- 입력 피처: (x, y, t, noise_event_flag, weather_temp, wind_speed)
- 출력: 2D grid probability map (matplotlib imshow 또는 folium)

**주의**: 모기 레포의 `AGENTS.md` HARD CONSTRAINTS 참고 — 특히 world-frame 손실 함수 변경 금지 원칙은 여기서도 유효.

### Phase 3 — LLM Radio Bridge

**아키텍처**:
```
PZ 게임 (Lua) → game_state.json 파일 write
→ bridge/radio_server.py (파일 감시 + Claude API 호출)
→ response.json 파일 write
→ PZ 게임 (Lua) → UI 텍스트 표시
```

**파일**: `bridge/radio_server.py`
- `watchdog` 라이브러리로 `game_state.json` 변경 감시
- Anthropic Python SDK로 Claude API 호출
- 프롬프트에 생존 일수, 날씨, 최근 킬 수 포함
- 응답을 `response.json`에 저장

---

## 공통 규칙

1. **브랜치**: 모든 작업은 `claude/blissful-rubin-CsLA5` 브랜치에서
2. **커밋 메시지**: `[claude]` 또는 `[antigravity]` 접두사로 작성자 구분
3. **data/raw/**: `.gitignore`에 등록 — 게임 세션 데이터는 커밋 금지
4. **스키마 먼저**: 새 데이터 형식 추가 시 `data/schemas/`에 정의 문서 먼저 작성
5. **mod.info require 필드**: Lua 모드는 의존성 없이 바닐라만으로 동작하도록 유지

---

## AI Mistakes Log

형식: `날짜 | 에이전트 | 실수 내용 | 영향 | 수정 방법 | 교훈`

| 날짜 | 에이전트 | 실수 | 영향 | 수정 | 교훈 |
|------|---------|------|------|------|------|
| (기록 없음) | — | — | — | — | — |

> 실수 발생 시 위 테이블에 추가. 같은 실수 반복 방지가 목적.

---

## 프로젝트 상태 체크리스트

- [ ] Phase 1: `DataDumper` Lua 모드 작성 (Claude)
- [ ] Phase 1: `nutrition_session_*.csv` 스키마 정의 (Claude)
- [ ] Phase 1: Nutrition Optimizer ILP 구현 (Antigravity)
- [ ] Phase 2: `ZombieLogger` Lua 모드 작성 (Claude)
- [ ] Phase 2: `zombie_log_*.csv` 스키마 정의 (Claude)
- [ ] Phase 2: Zombie Heatmap GRU 모델 (Antigravity)
- [ ] Phase 3: `RadioBridge` Lua 직렬화 (Claude)
- [ ] Phase 3: `bridge/radio_server.py` 구현 (Antigravity)
