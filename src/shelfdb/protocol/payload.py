"""Shared RPC payload logging helpers for ShelfDB."""

from __future__ import annotations

from typing import Any, cast


def payload_log_kwargs(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        return {"payload_type": type(payload).__name__}

    payload_dict = cast(dict[str, Any], payload)
    request_type = payload_dict.get("type")
    metadata: dict[str, object] = {"request_type": request_type}
    if request_type == "query":
        metadata["shelf"] = payload_dict.get("shelf")
        metadata["query_count"] = len(
            cast(list[object], payload_dict.get("queries", []))
        )
    elif request_type == "transaction":
        metadata["tx_count"] = len(cast(list[object], payload_dict.get("txs", [])))
        metadata["write"] = payload_dict.get("write")
    return metadata
