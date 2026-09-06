# Schema: noise_events_session_<id>.csv

Lua 모드 `NoiseLogger.lua`가 생성. `Events.OnPlayerAttackFinished` 훅으로
소음 발생 때마다 1행 추가 (이벤트 드리봐).

| 컴럼 | 타입 | 범위 | 설명 |
|------|------|------|------|
| `world_age_hours` | float | 0 ~ ∞ | 게임 누적 시간 — `player_stats` / `zombie_log`와 조인 키 |
| `source_x` | float | 0 ~ 15000 | 소음 발생 X 좌표 (플레이어 위치 기준) |
| `source_y` | float | 0 ~ 15000 | 소음 발생 Y 좌표 |
| `intensity` | float | 0 ~ ~80 | 소음 반경(셀). 무기 `SoundRadius` 값 |
| `noise_type` | string | `gunshot`, `melee`, ... | 이벤트 분류 |

## Antigravity 사용 노트

- Phase 2 좌비 히트맵의 핵심 입력 시그널
- 소음 이벤트 이후 `zombie_log`를 forward-window로 정렬하면 호드 이동 패턴 추적 가능
- `intensity`를 가중치로 사용해서 KDE radius를 가변화 가능
- Lua 쪽 `NoiseLogger.lua`는 현재 플레이어 공격만 훅. 좌비 고함도는 `Events.OnZombieDead`
  등을 추가해서 확장 가능 (추후 작업).
