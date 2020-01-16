.PHONY:

all: coverage typing

install-dev:
	pip install pytest pytest-cov mypy

test: clean-pyc
	pytest -v

coverage: clean-pyc
	pytest --cov=global_id -v
	coverage html

cov: coverage

typing: clean-pyc
	mypy --strict global_id.py

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +
