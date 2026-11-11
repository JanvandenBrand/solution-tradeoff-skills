.PHONY: check lint test

POETRY ?= poetry
SCRIPTS := skills/solution-tradeoff/scripts

check: lint test

lint:
	$(POETRY) run flake8 $(SCRIPTS) tests/
	$(POETRY) run black --check $(SCRIPTS) tests/
	$(POETRY) run bandit -r $(SCRIPTS) -q
	$(POETRY) run mypy $(SCRIPTS)

test:
	$(POETRY) run pytest --cov=$(SCRIPTS) --cov-report=term-missing --cov-fail-under=90 -q
