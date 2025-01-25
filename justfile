[private]
default:
  @just --list

# Sync development environment
sync:
  uv sync --group dev

# Run command within environment
run +args:
  uv run -- {{args}}

generate version:
  uv run scripts/generator.py --version {{version}}

# Print project version
version:
  @uvx --from setuptools-scm python -m setuptools_scm

build:
  uv build
  uvx check-wheel-contents dist/*-$(just version)-*.whl

# Run linter
lint:
  uvx ruff check --output-format concise

# Dry run formatter and output the diffs
fmt:
  uvx ruff format --diff

# Run mypy
mypy:
  uv sync --inexact --no-default-groups --group mypy
  uv run --no-sync -- mypy

# Run tests
test *args:
  uv sync --inexact --no-default-groups --group test
  uv run --no-sync -- pytest {{args}}

# Run tests and report coverage
testcov *args:
  uv sync --inexact --no-default-groups --group test --group cov
  uv run --no-sync -- coverage run -m pytest {{args}}
  uv run --no-sync -- coverage report
