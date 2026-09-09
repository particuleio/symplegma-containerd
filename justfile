set shell := ["mise", "exec", "--", "bash", "-euo", "pipefail", "-c"]

default:
    @just --list

setup:
    uv sync --locked
    uv run --locked pre-commit install

lint:
    uv run --locked pre-commit run --all-files --show-diff-on-failure

# Render both OCI runtime configurations without Docker or a live cluster.
unit:
    uv run --locked python -m unittest discover -s tests -v

# Disposable privileged Docker containers; do not run on a production host.
test:
    uv run --locked molecule test
