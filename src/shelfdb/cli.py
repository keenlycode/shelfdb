"""Command-line interface for ShelfDB."""

from __future__ import annotations

import shutil
import sysconfig
from contextlib import suppress
from pathlib import Path

from cyclopts import App

from shelfdb.protocol import serve, serve_unix
from shelfdb.shelf import DB
from shelfdb.target import parse_target, parse_tcp_location, parse_unix_location

app = App("shelfdb")
DEFAULT_AI_SKILL_INSTALL_PATH = ".agents/skills/shelfdb-usage"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def bundled_ai_skill_path() -> Path:
    data_root = Path(sysconfig.get_path("data"))
    installed_path = data_root / "shelfdb-usage"
    if installed_path.exists():
        return installed_path

    repo_path = repo_root() / "ai-skill" / "shelfdb-usage"
    if repo_path.exists():
        return repo_path

    raise FileNotFoundError("Bundled ShelfDB AI skill not found.")


def install_ai_skill(destination: Path) -> Path:
    source = bundled_ai_skill_path()
    if destination.exists():
        shutil.rmtree(destination)

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    return destination


def prompt_ai_skill_install_path(default_path: str = DEFAULT_AI_SKILL_INSTALL_PATH) -> Path:
    response = input(f"Install ShelfDB AI skill to [{default_path}]: ").strip()
    return Path(response or default_path)


async def run_server(
    *,
    db_path: str,
    url: str = "tcp://127.0.0.1:31337",
) -> None:
    scheme, location = parse_target(url)
    socket_path = None

    with DB(db_path) as db:
        if scheme == "tcp":
            host, port = parse_tcp_location(location)
            server = await serve(db, host=host, port=port)
        else:
            socket_path = str(Path(parse_unix_location(location)))
            server = await serve_unix(db, path=socket_path)

        try:
            await server.serve_forever()
        finally:
            server.close()
            await server.wait_closed()
            if socket_path is not None:
                with suppress(FileNotFoundError):
                    Path(socket_path).unlink()


@app.command
async def server(
    db_path: str = "db",
    url: str = "tcp://127.0.0.1:31337",
) -> None:
    """Run the ShelfDB protocol server."""
    await run_server(db_path=db_path, url=url)


@app.command(name="ai-skill-install")
def ai_skill_install(path: str | None = None) -> None:
    """Install the bundled ShelfDB AI skill to a local path."""
    destination = Path(path) if path is not None else prompt_ai_skill_install_path()
    installed = install_ai_skill(destination)
    print(f"Installed ShelfDB AI skill to {installed}")


def main(argv: list[str] | None = None) -> None:
    app(argv, backend="asyncio", result_action="return_none")
