# Installation

## Requirements

- Python 3.12–3.14

## Install for development

The repository selects Python 3.14 via `.python-version`; compatibility checks
run on Python 3.12 and 3.14. Python 3.15 is temporarily excluded because the
released `dill` cannot serialize query callbacks on it. Support will be
reassessed after an upstream fix is released.

Using `uv`:

```bash
uv sync
```

This installs the package plus the development dependencies, including Zensical.

## Install the package only

Using `uv`:

```bash
uv pip install .
```

Using `pip`:

```bash
pip install .
```

## Verify the CLI

```bash
shelfdb server --help
```
