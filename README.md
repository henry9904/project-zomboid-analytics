# Project Zomboid Analytics

인게임 데이터를 Lua 모딩으로 추출하고, Python/PyTorch로 분석·예측하는 포트폴리오 프로젝트.

## 프로젝트 구조

```
project-zomboid-analytics/
├── lua-mods/           # Claude 담당 — 인게임 데이터 추출 모드
│   ├── DataDumper/     # 핵심 모드: 좀비/플레이어 데이터 → CSV/JSON
│   └── RadioBridge/    # LLM 라디오 모드 Lua 쪽 (Phase 3)
├── data/
│   ├── raw/            # Lua 모드가 덤프한 원본 파일 (gitignore)
│   ├── processed/      # Antigravity가 전처리한 DataFrame
│   └── schemas/        # CSV/JSON 스키마 정의 문서
├── analysis/notebooks/ # Antigravity 담당 — EDA 노트북
├── models/             # Antigravity 담당 — PyTorch 모델
└── bridge/             # Python ↔ Lua HTTP 브릿지 (Phase 3)
```

## 3단계 로드맵

| Phase | 아이디어 | Claude (Lua) | Antigravity (Python) | 상태 |
|-------|---------|-------------|---------------------|------|
| 1 | Nutrition Optimizer | 플레이어 스탯 + 인벤토리 덤프 | 최적 식단 TSP/휴리스틱 | 🚀 진행 중 |
| 2 | Zombie Heatmap | 좀비 좌표 샘플링 로거 | 시계열 히트맵 (GRU) | 📋 예정 |
| 3 | LLM Radio Mod | 게임 상태 JSON 직렬화 | Python HTTP 브릿지 서버 | 📋 예정 |

## 공통 추출 가능 데이터 (바닐라 안전)

어떤 모드 조합을 쓰더라도 아래 데이터는 PZ 기본 API로 항상 접근 가능:

| 데이터 | Lua API | 비고 |
|--------|---------|------|
| 플레이어 위치 (x,y,z) | `getPlayer():getX/Y/Z()` | 셀 좌표 |
| 체력/허기/갈증/피로 | `getPlayer():getBodyDamage()` | BodyDamage 객체 |
| 칼로리/체중 | `getPlayer():getNutrition()` | Nutrition 모듈 필요 |
| 스트레스/공황/지루함 | `getPlayer():getStats()` | Stats 객체 |
| 게임 날짜·시간 | `getGameTime():getWorldAgeHours()` | 실수형 게임 시각 |
| 날씨 (온도/비/안개) | `getClimateManager()` | 기후 상태 전반 |
| 좀비 위치 목록 | `getCell():getZombieList()` | 셀 단위 리스트 |
| 인벤토리 아이템 | `getPlayer():getInventory()` | 아이템 타입·수량 |
| 소음 이벤트 | `Events.OnNoise` 훅 | 이벤트 기반 |
| 좀비 사망 이벤트 | `Events.OnZombieDead` 훅 | 이벤트 기반 |

## 역할 분담

- **Crong (Tech Lead)**: 기획, 방향 설정, 최종 QA
- **Claude**: Lua 모딩 전담 — `lua-mods/` 작성·디버그
- **Antigravity**: Python 전담 — `data/`, `analysis/`, `models/` 작업

## 개발 환경

- Project Zomboid: Build 41.x (Steam, IWBUMS 브랜치 또는 stable)
- 모드 경로: `%ProgramFiles(x86)%/Steam/steamapps/common/ProjectZomboid/mods/`
- Python: 3.10+, PyTorch 2.x, pandas, matplotlib
