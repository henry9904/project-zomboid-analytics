# Schema: datadumper_zombie_log.csv

Lua 모드 `ZombieLogger.lua`가 생성. 6 게임시간마다 플레이어 50셀 반경 내 좀비 샘플링.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `world_age_hours` | float | 게임 누적 시간 — `player_stats`와 조인 키 |
| `zx` | float | 좀비 월드 X 좌표 |
| `zy` | float | 좀비 월드 Y 좌표 |
| `zz` | float | 좀비 층 (보통 0) |
| `state` | string | 좀비 상태 코드 (예: `0`=wandering, `3`=chasing 등 — 버전별 상이) |

## Antigravity 사용 노트

- 같은 `world_age_hours`의 행들이 하나의 스냅샷
- 히트맵 생성: `zx`, `zy`로 KDE → matplotlib `imshow` 또는 seaborn `kdeplot`
- 시계열 예측: `world_age_hours` 기준으로 연속 스냅샷 → GRU 입력
- 소음 이벤트(`noise_events.csv`)의 `world_age_hours`와 조인하면 이벤트 후 좀비 이동 패턴 분석 가능
- **좌표계 주의**: PZ 월드 좌표는 (0,0) = 북서쪽 코너, Y 증가 = 남쪽 이동 (이미지 좌표계와 동일)
