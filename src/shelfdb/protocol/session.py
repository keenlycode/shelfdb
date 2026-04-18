"""Per-connection session state for the ShelfDB protocol POC."""

from __future__ import annotations

from typing import Any

from shelfdb.shelf import DB, Item, MutationResult


def _ok(result: Any = None) -> dict[str, Any]:
    response = {"ok": True}
    if result is not None:
        response["result"] = result
    return response


def _error(message: str) -> dict[str, Any]:
    return {"ok": False, "error": message}


def _normalize_result(result: Any) -> Any:
    if isinstance(result, Item):
        return {"key": result.key, "value": result.value}
    if isinstance(result, MutationResult):
        return {"key": result.key, "ok": result.ok}
    return result


class Session:
    """Handle simple protocol commands against one current transaction."""

    def __init__(self, db: DB):
        self._db = db
        self._tx: Any | None = None
        self._mode: str | None = None

    @property
    def active(self) -> bool:
        return self._tx is not None

    @property
    def mode(self) -> str | None:
        return self._mode

    def handle(self, command: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(command, dict):
            return _error("command must be a dict")

        name = command.get("cmd")

        if name == "begin":
            if self.active:
                return _error("transaction already active")
            return self._begin(command.get("mode"))

        if name not in {"put", "get", "commit", "rollback"}:
            return _error("unknown command")

        if not self.active:
            return _error("no active transaction")

        if name == "commit":
            return self._commit()

        if name == "rollback":
            return self._rollback()

        try:
            if name == "put":
                return self._put(
                    shelf=command["shelf"],
                    key=command["key"],
                    value=command["value"],
                )
            return self._get(shelf=command["shelf"], key=command["key"])
        except Exception as exc:
            return _error(str(exc))

    def close(self) -> None:
        if self.active:
            self._tx.tx.abort()
            self._clear_transaction()

    def _begin(self, mode: str | None) -> dict[str, Any]:
        if mode not in {"read", "write"}:
            return _error("unsupported transaction mode")

        self._tx = self._db.transaction(write=mode == "write")
        self._mode = mode
        return _ok({"mode": mode})

    def _put(self, *, shelf: str, key: str, value: Any) -> dict[str, Any]:
        result = self._tx.shelf(shelf).put(key, value)
        return _ok(_normalize_result(result))

    def _get(self, *, shelf: str, key: str) -> dict[str, Any]:
        result = self._tx.shelf(shelf).key(key).item()
        return _ok(_normalize_result(result))

    def _commit(self) -> dict[str, Any]:
        if self._tx.is_write:
            self._tx.commit()
        else:
            self._tx.tx.abort()
        self._clear_transaction()
        return _ok({"committed": True})

    def _rollback(self) -> dict[str, Any]:
        self._tx.tx.abort()
        self._clear_transaction()
        return _ok({"rolled_back": True})

    def _clear_transaction(self) -> None:
        self._tx = None
        self._mode = None
