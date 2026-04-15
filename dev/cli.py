"""Development utilities for ShelfDB."""

from __future__ import annotations

from pathlib import Path
import shutil

from cyclopts import App


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DOCS = ROOT / "docs-src"
MIRROR_DOCS = (
    ROOT / "src" / "shelfdb" / "ai_skill" / "shelfdb-usage" / "references" / "docs"
)


app = App(help="ShelfDB development utilities")


def _markdown_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.md") if path.is_file())


def _mirror_path(source_path: Path) -> Path:
    return MIRROR_DOCS / source_path.relative_to(SOURCE_DOCS)


@app.command(name="ai-skill-mkdocs")
def ai_skill_mkdocs():
    """Mirror docs-src Markdown files into the ShelfDB AI skill references tree."""

    if not SOURCE_DOCS.exists():
        raise FileNotFoundError(f"Missing docs source directory: {SOURCE_DOCS}")

    source_relpaths = {
        path.relative_to(SOURCE_DOCS) for path in _markdown_files(SOURCE_DOCS)
    }
    copied = 0
    removed = 0
    unchanged = 0

    MIRROR_DOCS.mkdir(parents=True, exist_ok=True)

    for source_path in _markdown_files(SOURCE_DOCS):
        destination_path = _mirror_path(source_path)
        destination_path.parent.mkdir(parents=True, exist_ok=True)

        if (
            destination_path.exists()
            and destination_path.read_bytes() == source_path.read_bytes()
        ):
            unchanged += 1
            continue

        shutil.copy2(source_path, destination_path)
        copied += 1

    for destination_path in sorted(
        MIRROR_DOCS.rglob("*"),
        key=lambda path: len(path.relative_to(MIRROR_DOCS).parts),
        reverse=True,
    ):
        relative_path = destination_path.relative_to(MIRROR_DOCS)
        if destination_path.is_file() and relative_path not in source_relpaths:
            destination_path.unlink()
            removed += 1

    for destination_path in sorted(
        MIRROR_DOCS.rglob("*"),
        key=lambda path: len(path.relative_to(MIRROR_DOCS).parts),
        reverse=True,
    ):
        if not destination_path.is_dir() or destination_path == MIRROR_DOCS:
            continue
        try:
            next(destination_path.iterdir())
        except StopIteration:
            destination_path.rmdir()

    print(f"ai-skill-mkdocs: {copied} copied, {removed} removed, {unchanged} unchanged")


def main(tokens: list[str] | None = None):
    app(tokens)


if __name__ == "__main__":
    main()
