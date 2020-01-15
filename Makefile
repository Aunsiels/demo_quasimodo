PYTHON ?= python3
PYTEST ?= pytest
PYLINT ?= pylint

.EXPORT_ALL_VARIABLES:

PYTHONPATH = PYTHONPATH:$(pwd)

test-code:
	$(PYTEST) --showlocals -v quasimodo_website

test-code-xml:
	$(PYTEST) --showlocals -v quasimodo_website --junit-xml test-reports/results.xml

test-code-profiling:
	$(PYTEST) --showlocals -v quasimodo_website --profile

test-code-profiling-svg:
	$(PYTEST) --showlocals -v quasimodo_website --profile-svg

test-coverage:
		rm -rf coverage .coverage
		$(PYTEST) quasimodo_website --showlocals -v --cov=quasimodo_website --cov-report=html:coverage

test-coverage-xml:
		rm -rf reports/coverage.xml
		$(PYTEST) quasimodo_website --showlocals -v --cov=quasimodo_website --cov-report=xml:reports/coverage.xml

style-check:
	$(PYLINT) --rcfile=pylint.cfg quasimodo_website > pylint.report || true
	pycodestyle quasimodo_website > pep8.report || true

build:
	rm -f dist/*
	$(PYTHON) setup.py sdist bdist_wheel

clean:
	rm -rf coverage .coverage
	$(MAKE) -C doc clean

.PHONY: clean build style-check
