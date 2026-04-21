# Installation

## Requirements

- Python 3.12+

## Install for development

Using `uv`:

```bash
uv sync
```

This installs the package plus the development dependencies, including MkDocs.

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
