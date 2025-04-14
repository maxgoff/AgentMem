.PHONY: test clean install dev

test:
	pytest

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

install:
	pip install -e .

dev:
	pip install -e ".[dev]"