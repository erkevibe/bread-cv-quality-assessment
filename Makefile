PYTHON ?= .venv/bin/python

.PHONY: install test lint audit experiment word clean

install:
	uv sync --extra dev --extra cnn

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check src scripts tests

audit:
	$(PYTHON) scripts/audit_dataset.py --config configs/experiment.yaml

experiment:
	$(PYTHON) scripts/run_all.py --config configs/experiment.yaml

word:
	npm install
	npm run article:word

clean:
	$(PYTHON) scripts/clean_generated.py
