# Schema: datadumper_player_stats.csv

Lua 모드 `PlayerStatsLogger.lua`가 생성. 2 게임시간마다 1행 추가.

| 컬럼 | 타입 | 범위 | 설명 |
|------|------|------|------|
| `world_age_hours` | float | 0 ~ ∞ | 게임 시작 이후 누적 게임시간(시) — 기본 타임스탬프 |
| `day` | int | 0 ~ ∞ | 생존 일수 (0-indexed) |
| `hour` | float | 0.0 ~ 23.99 | 게임 내 현재 시각(시) |
| `x` | float | — | 플레이어 월드 X 좌표 (셀 단위) |
| `y` | float | — | 플레이어 월드 Y 좌표 (셀 단위) |
| `z` | float | 0, 1, 2, 3 | 층 (0 = 지상) |
| `hunger` | float | 0.0 ~ 1.0 | 허기 (1.0 = 최대 허기 = 굶주림) |
| `thirst` | float | 0.0 ~ 1.0 | 갈증 (1.0 = 극도 갈증) |
| `fatigue` | float | 0.0 ~ 1.0 | 피로 (1.0 = 극도 피로) |
| `stress` | float | 0.0 ~ 1.0 | 스트레스 |
| `panic` | float | 0.0 ~ 1.0 | 공황 |
| `boredom` | float | 0.0 ~ 1.0 | 지루함 |
| `calories` | float | 0 ~ ~3000 | 현재 칼로리 잔량 (kcal) |
| `weight` | float | ~35 ~ ~120 | 체중 (kg) |
| `carbs` | float | 0 ~ ~500 | 탄수화물 섭취량 잔량 (g) |
| `protein` | float | 0 ~ ~500 | 단백질 (g) |
| `fat` | float | 0 ~ ~500 | 지방 (g) |

## Antigravity 사용 노트

- `world_age_hours`를 기본 인덱스로 사용
- `hunger`, `thirst`는 역수 관계: 낮을수록 좋음 (0 = 포만감)
- `calories`는 마지막 식사 이후 감소 — 하루 소모량 계산 가능
- `weight` 변화율이 근손실/비만 지표 → Nutrition Optimizer의 핵심 타겟
