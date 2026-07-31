import asyncio

from shelfdb.protocol.demo_poc import run_demo


def test_demo_poc_runs_end_to_end(tmp_path):
    result = asyncio.run(run_demo(str(tmp_path / "shelfdb")))

    assert result["written"] == {"key": "a", "ok": True}
    assert result["item"] == {"key": "a", "value": {"name": "hello"}}
