PY = poetry run python

.PHONY: install dev run

install:
	poetry install

dev:
	poetry run uvicorn position_svc.server:app --host 0.0.0.0 --port 4000 --reload

run:
	poetry run uvicorn position_svc.server:app --host 0.0.0.0 --port 4000


