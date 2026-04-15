"""Cyclopts-powered CLI entrypoint for ShelfDB server and skills."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path
import shutil
import sys
from typing import cast

from cyclopts import App

from .log import configure_logging
from .server import ShelfServer
from .util.transport import parse_transport_url


SKILL_SOURCE_PACKAGE = "shelfdb.ai_skill"
SKILL_SOURCE_NAME = "shelfdb-usage"
DEFAULT_SKILL_INSTALL_PATH = Path(".agents/skills") / SKILL_SOURCE_NAME


@dataclass(frozen=True, slots=True)
class ServerConfig:
    url: str = "tcp://127.0.0.1:17000"
    db: str = "db"
    log_level: str = "info"

    def __post_init__(self):
        if not self.db.strip():
            raise ValueError("db must not be empty")
        parse_server_url(self.url)


def parse_server_url(url: str) -> tuple[str, str | int]:
    """Parse a TCP or Unix server URL into transport-specific values."""
    return parse_transport_url(
        url,
        tcp_hostname_message="tcp URL must include a hostname",
        tcp_port_message="tcp URL must include a port",
        unix_path_message="unix URL must include a socket path",
        scheme_message="url must use tcp:// or unix:// scheme",
    )


app = App(help="ShelfDB server and skill utilities")


def _serve(url: str = "tcp://127.0.0.1:17000", db: str = "db", log_level: str = "info"):
    config = ServerConfig(url=url, db=db, log_level=log_level)
    configure_logging(config.log_level)
    transport, value = parse_server_url(config.url)
    if transport == "unix":
        shelf_server = ShelfServer(
            host=None, port=None, db_name=config.db, unix_path=cast(str, value)
        )
    else:
        shelf_server = ShelfServer(cast(str, transport), cast(int, value), config.db)

    if sys.platform.startswith("linux"):
        import uvloop

        uvloop.install()

    try:
        asyncio.run(shelf_server.run())
    except KeyboardInterrupt:
        pass


@app.default
def serve(url: str = "tcp://127.0.0.1:17000", db: str = "db", log_level: str = "info"):
    _serve(url=url, db=db, log_level=log_level)


@app.command(name="server")
def server(url: str = "tcp://127.0.0.1:17000", db: str = "db", log_level: str = "info"):
    _serve(url=url, db=db, log_level=log_level)


def _skill_source_root() -> Traversable:
    return resources.files(SKILL_SOURCE_PACKAGE).joinpath(SKILL_SOURCE_NAME)


def _copy_resource_tree(source: Traversable, destination: Path):
    if source.is_dir():
        destination.mkdir(parents=True, exist_ok=False)
        for child in source.iterdir():
            _copy_resource_tree(child, destination / child.name)
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as reader, destination.open("wb") as writer:
        shutil.copyfileobj(reader, writer)


@app.command(name="skill-install")
def skill_install(path: Path | None = None):
    """Install the bundled ShelfDB AI skill into a Codex skills directory."""

    destination = path or DEFAULT_SKILL_INSTALL_PATH
    if destination.exists():
        raise FileExistsError(
            f"Skill already exists at {destination}. Use --path to choose another destination."
        )

    skill_source = _skill_source_root()
    if not skill_source.is_dir():
        raise FileNotFoundError(
            f"Missing bundled skill resources: {SKILL_SOURCE_PACKAGE}/{SKILL_SOURCE_NAME}"
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    _copy_resource_tree(skill_source, destination)
    print(f"Installed {SKILL_SOURCE_NAME} to {destination}")


def main(tokens: list[str] | None = None):
    app(tokens, result_action="return_none")
