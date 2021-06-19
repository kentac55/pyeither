SHELL=/bin/bash

.PHONY: help
help: ## Show this message
	# Thanks @po3rin(https://qiita.com/po3rin/items/7875ef9db5ca994ff762)
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: lint
lint: ## Run linters
	@poetry run mypy --strict -p pyeither -p tests
	@poetry run black --check .
	@poetry run isort -c .
	@poetry run pylint pyeither

.PHONY: fix
fix:  ## Run fixers
	@poetry run black .
	@poetry run isort .

.PHONY: test
test: ## Run unittest
	@poetry run pytest --cov=pyeither --cov-report=xml --cov-report=term-missing -vv -W default tests

.PHONY: build
build: ## Create wheel package
	@poetry build

.PHONY: publish
publish:  ## Publish package to PyPi
	@poetry publish
