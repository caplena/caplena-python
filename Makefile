.DEFAULT_GOAL := help
.PHONY: help docs

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

lint: ## Run code linters
	black .
	isort .
	flake8 .
	mypy .

fmt format: ## Run code formatters
	black ninja tests
	isort ninja tests

test: ## Run tests
	pytest .

test-watch: ## Run tests in watching mode
	ptw -w
