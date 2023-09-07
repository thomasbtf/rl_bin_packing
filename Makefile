#* Variables
SHELL := /usr/bin/env bash
PYTHON := python
PYTHONPATH := `pwd`

#* Docker variables
IMAGE := rlbinpacking
VERSION := rlbinpacking

#* Poetry
.PHONY: poetry-download
poetry-download:
	curl -sSL https://install.python-poetry.org | $(PYTHON) -

.PHONY: poetry-remove
poetry-remove:
	curl -sSL https://install.python-poetry.org | $(PYTHON) - --uninstall

.PHONY: poetry-install
poetry-install:
	poetry lock -n
	poetry install

.PHONY: mypy-install
mypy-install:
	poetry run mypy --install-types --non-interactive ./

#* Installation
.PHONY: install
install: poetry-install mypy-install

#* Formatters
.PHONY: codestyle
codestyle:
	poetry run black --config pyproject.toml ./
	poetry run ruff . --fix 

.PHONY: formatting
formatting: codestyle

#* Linting
.PHONY: test
test:
	PYTHONPATH=$(PYTHONPATH) poetry run pytest -c pyproject.toml --junitxml=report.xml --cov-report term  --cov-report html --cov-report xml:coverage.xml --cov=rl_bin_packing tests/

.PHONY: check-codestyle
check-codestyle:
	poetry run black --diff --check --config pyproject.toml ./ 
	poetry run darglint --verbosity 2 rl_bin_packing tests
	poetry run ruff .

.PHONY: mypy
mypy:
	poetry run mypy --config-file pyproject.toml ./

.PHONY: lint
lint: test check-codestyle mypy

.PHONY: update-dev-deps
update-dev-deps:
	poetry add --group dev pytest@latest pytest-html@latest pytest-cov@latest black@latest ruff@latest darglint@latest mypy-extensions@latest mypy@latest

.PHONY: build
build:
	poetry build


#* Docker
# Example: make docker-build VERSION=latest
# Example: make docker-build IMAGE=some_name VERSION=0.1.0
.PHONY: docker-build
docker-build:
	@echo Building docker $(IMAGE):$(VERSION) ...
	docker build \
		-t $(IMAGE):$(VERSION) . \
		-f ./docker/Dockerfile --no-cache

# Example: make docker-remove VERSION=latest
# Example: make docker-remove IMAGE=some_name VERSION=0.1.0
.PHONY: docker-remove
docker-remove:
	@echo Removing docker $(IMAGE):$(VERSION) ...
	docker rmi -f $(IMAGE):$(VERSION)

#* Cleaning
.PHONY: pycache-remove
pycache-remove:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

.PHONY: dsstore-remove
dsstore-remove:
	find . | grep -E ".DS_Store" | xargs rm -rf

.PHONY: mypycache-remove
mypycache-remove:
	find . | grep -E ".mypy_cache" | xargs rm -rf

.PHONY: ipynbcheckpoints-remove
ipynbcheckpoints-remove:
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf

.PHONY: pytestcache-remove
pytestcache-remove:
	find . | grep -E ".pytest_cache" | xargs rm -rf

.PHONY: ruffcache-remove
ruffcache-remove:
	find . | grep -E ".ruff_cache" | xargs rm -rf

.PHONY: htmlcov-remove
htmlcov-remove:
	find . | grep -E "htmlcov" | xargs rm -rf

.PHONY: coverage-remove
coverage-remove:
	find . | grep -E ".coverage" | xargs rm -rf
	find . | grep -E "coverage.xml" | xargs rm -rf
	find . | grep -E "report.xml" | xargs rm -rf
	
.PHONY: build-remove
build-remove:
	rm -rf build/
	rm -rf dist/

.PHONY: cleanup
cleanup: pycache-remove dsstore-remove mypycache-remove ipynbcheckpoints-remove pytestcache-remove ruffcache-remove htmlcov-remove coverage-remove build-remove