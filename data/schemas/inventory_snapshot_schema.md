# Schema: inventory_snapshot_session_<id>.csv

Lua 모드 `InventoryLogger.lua`가 생성. 2 게임시간마다 플레이어 인벤토리의
식품 아이템을 집계해 1행씩 출력. 동일 `item_type`은 합산.

| 컴럼 | 타입 | 설명 |
|------|------|------|
| `world_age_hours` | float | 게임 누적 시간 |
| `item_type` | string | PZ item id (예: `Base.Bread`, `Base.Steak`) |
| `count` | int | 현재 보유 수량 |
| `calories_per_unit` | float | 한 단위당 칼로리(kcal) |
| `carbs_per_unit` | float | 한 단위당 탄수화물(g) |
| `protein_per_unit` | float | 한 단위당 단백질(g) |
| `fat_per_unit` | float | 한 단위당 지방(g) |

## Antigravity 사용 노트

- Phase 1 Nutrition Optimizer의 결정 변수(보유량) + 영양 계수 동시 제공
- 게임 진행에 따라 `count`가 줄어듦 → 시계열로 보면 식량 소모율(burn rate) 산출
- 같은 (session_id, world_age_hours, item_type) 조합은 1행만 생성됨 (Lua 측 집계)
- 영양 계수(per_unit) 값은 아이템이 처음 집계될 때 스냅샷. 모드된 음식이 아니라면
  세션 내 동일 `item_type` 에 대해 변하지 않음
