.DEFAULT_GOAL := help
.PHONY: help docs

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## Installs all dependencies
	flit install --deps develop --symlink
	pre-commit

lint: ## Run code linters
	ruff check .
	ruff format --check .
	mypy caplena tests --install-types --non-interactive

fmt format: ## Run code formatters
	ruff check . --fix
	ruff format .

test: ## Run tests
	pytest .

test-watch: ## Run tests in watching mode
	ptw -w

build-docs: ## Builds Sphinx HTML docs
	cd docs && $(MAKE) html

build-sdk: ## Builds the Python SDK
	flit build

publish-sdk: ## Publishes the Python SDK
	flit publish
