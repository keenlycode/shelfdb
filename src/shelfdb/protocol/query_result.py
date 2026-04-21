"""Normalization helpers for remote query results."""

from __future__ import annotations

from typing import Any

from shelfdb.shelf import UNDEF, Item, MutationResult

_TYPE_KEY = "__shelfdb_type__"


def normalize_query_result(result: Any) -> Any:
    if result is UNDEF:
        return {_TYPE_KEY: "undef"}
    if isinstance(result, Item):
        return {
            _TYPE_KEY: "item",
            "key": result.key,
            "value": normalize_query_result(result.value),
        }
    if isinstance(result, MutationResult):
        return {
            _TYPE_KEY: "mutation",
            "key": result.key,
            "ok": result.ok,
        }
    if isinstance(result, tuple):
        return [normalize_query_result(value) for value in result]
    if isinstance(result, list):
        return [normalize_query_result(value) for value in result]
    if isinstance(result, dict):
        return {key: normalize_query_result(value) for key, value in result.items()}
    return result


def denormalize_query_result(result: Any) -> Any:
    if isinstance(result, list):
        return [denormalize_query_result(value) for value in result]
    if not isinstance(result, dict):
        return result

    marker = result.get(_TYPE_KEY)
    if marker == "undef":
        return UNDEF
    if marker == "item":
        return Item(result["key"], denormalize_query_result(result["value"]))
    if marker == "mutation":
        return MutationResult(result["key"], result["ok"])
    return {key: denormalize_query_result(value) for key, value in result.items()}
