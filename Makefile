.PHONY: check lint test package

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

package:
	rm -rf dist && mkdir -p dist
	cd skills && zip -rq ../dist/solution-tradeoff.zip solution-tradeoff \
		-x '*/__pycache__/*' '*.pyc'
