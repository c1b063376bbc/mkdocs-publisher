# Contributing

Thanks for helping improve Publisher for MkDocs. This project is a set of MkDocs plugins, so most changes should stay
small, focused and covered by tests close to the plugin or helper they touch.

## Development Setup

Install `uv`, then prepare the development environment:

```bash
uv python install 3.9
uv sync --group dev --group test
```

Run the test suite with:

```bash
uv run pytest
```

Run the same style and safety checks used by pull requests with:

```bash
uv run ruff format .
uv run ruff check .
uv run pyright
uv run yamllint .
```

## Pre-commit

The repository uses pre-commit for formatting, linting, type checking, tests and license headers:

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

One local hook, `check-readme-md`, copies `README.md` from the separate documentation repository path
`../mkdocs-publisher-docs/mkdocs_publisher_docs/README.md`. If you do not have that checkout locally, skip that hook:

```bash
SKIP=check-readme-md uv run pre-commit run --all-files
```

## Tests

Add or update tests for behavior changes. Keep tests near the area they cover:

- shared helpers: `tests/_shared/`
- plugin behavior: `tests/<plugin-name>/`
- CLI behavior: `tests/cli/`

Pull requests run tests on Python 3.9 through 3.13. The project supports Python 3.9+, so avoid syntax or typing
features that require newer Python versions.

## Plugin Changes

When adding a plugin or a new plugin entry point:

- add the implementation under `mkdocs_publisher/<plugin-name>/`
- register it in `[project.entry-points."mkdocs.plugins"]` in `pyproject.toml`
- add focused tests under `tests/<plugin-name>/`
- document the minimal setup in `README.md` or the documentation project

When changing shared helpers, check the callers in multiple plugins. Some helpers are used during MkDocs config
loading, so keep imports lightweight and avoid doing filesystem or network work at import time.

## CLI Changes

CLI commands live in `mkdocs_publisher/_cli/plugins/` and are loaded automatically by `mkdocs-pub`. Add tests under
`tests/cli/` with `click.testing.CliRunner`.

Keep CLI module imports light. Commands should import MkDocs-heavy modules inside the command function when possible,
so `mkdocs-pub --help` can stay fast and robust.

## Documentation

User-facing behavior changes should update documentation. In this checkout, `README.md` is the local documentation
surface, but the project also has a separate documentation site repository. If you have both repos locally, update the
documentation source first and let the pre-commit hook sync `README.md`.

## Pull Requests

Before opening a pull request:

- keep the change scoped to one feature or fix
- run tests and relevant pre-commit checks
- include a short description of the behavior change
- mention any follow-up work or known limitations
- update `cov.json` only when running the full coverage workflow intentionally
