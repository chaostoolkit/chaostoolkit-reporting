.PHONY: install
install:
	pip install --upgrade pip setuptools wheel
	pip install -r requirements.txt

.PHONY: install-dev
install-dev: install
	pip install -r requirements-dev.txt
	python setup.py develop

.PHONY: build
build:
	python setup.py build

.PHONY: lint
lint:
	flake8 chaosreport/
	isort --check-only --profile black chaosreport/
	black --check --diff --line-length=80 chaosreport/

.PHONY: format
format:
	isort --profile black chaosreport/
	black --line-length=80 chaosreport/

.PHONY: tests
tests:
	pytest
