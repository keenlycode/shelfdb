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

## Optional AI skill

Install ShelfDB's compact usage skill for compatible coding agents:

```bash
shelfdb ai-skill-install
```

The command prompts for a destination and defaults to
`.agents/skills/shelfdb-usage`. Use `--path` for another agent convention. An
existing destination is preserved unless replacement is explicitly requested:

```bash
shelfdb ai-skill-install --path .agents/skills/shelfdb-usage --force
```

The skill provides quick guidance and links to these docs; it is not required to
use ShelfDB.
