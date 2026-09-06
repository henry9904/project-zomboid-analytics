.PHONY: install etl test lint dashboard watch clean

install:
	pip install -r requirements.txt

etl:
	python -m etl --input data/raw --db data/processed/zomboid.db --verbose

etl-fixtures:
	python -m etl --input tests/fixtures --db /tmp/zomboid.db --verbose

test:
	pytest -q

lint:
	ruff check .

dashboard:
	streamlit run dashboard/app.py -- --db data/processed/zomboid.db

watch:
	python -m etl.watchdog_runner --input data/raw --db data/processed/zomboid.db

clean:
	rm -rf data/processed/*.db __pycache__ .pytest_cache
