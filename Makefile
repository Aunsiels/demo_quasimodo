PYTHON ?= python3
PYTEST ?= pytest
PYLINT ?= pylint

.EXPORT_ALL_VARIABLES:

PYTHONPATH = PYTHONPATH:$(pwd)

test-code:
	$(PYTEST) --showlocals -v demo

test-code-xml:
	$(PYTEST) --showlocals -v demo --junit-xml test-reports/results.xml

test-code-profiling:
	$(PYTEST) --showlocals -v demo --profile

test-code-profiling-svg:
	$(PYTEST) --showlocals -v demo --profile-svg

test-coverage:
		rm -rf coverage .coverage
		$(PYTEST) demo --showlocals -v --cov=pyformlang --cov-report=html:coverage

test-coverage-xml:
		rm -rf reports/coverage.xml
		$(PYTEST) demo --showlocals -v --cov=pyformlang --cov-report=xml:reports/coverage.xml

style-check:
	$(PYLINT) --rcfile=pylint.cfg demo > pylint.report || true
	pycodestyle demo > pep8.report || true

clean:
	rm -rf coverage .coverage
	$(MAKE) -C doc clean

.PHONY: clean
