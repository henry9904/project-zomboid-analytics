# Streamlit dashboard

Warehouse 시각화 레이어. 세션별 칼로리·체중 추이, 스트레스 곡선, 좌비 sighting density,
noise event 로그를 해당 세션으로 필터해서 보여준다.

## 실행

    streamlit run dashboard/app.py -- --db data/processed/zomboid.db

`--` 잤복부는 Streamlit 필수 구문. 더브우이를 그 다음으로 넘긴다.

## CI 여부

CI에서는 띄우지 않는다 (시각적 검증은 대시보드의 목적이 아니므로). 대신
`data-quality.yml` 워크플로가 pipeline 궄레 + 테이블 row count 검증 + pytest 를
돌려서 그래프 소스의 품질을 지킨다.
