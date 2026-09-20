"""Import boundaries need fresh interpreters, not an already populated sys.modules."""

import subprocess
import sys
import textwrap

import pytest


@pytest.mark.parametrize(
    "statement",
    [
        "import shelfdb.protocol",
        "from shelfdb.client import Client",
        "from shelfdb.protocol import read_response, write_request",
        "from shelfdb.protocol.protocol import read_response, write_request",
    ],
)
def test_client_and_wire_imports_do_not_load_server_modules(statement):
    subprocess.run(
        [
            sys.executable,
            "-c",
            statement
            + "\nimport sys\n"
            + "assert not {'shelfdb.protocol.server', 'shelfdb.protocol.session', "
            "'shelfdb.protocol.write_admission'} & sys.modules.keys()",
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )


def test_public_server_exports_remain_compatible():
    subprocess.run(
        [
            sys.executable,
            "-c",
            textwrap.dedent("""
                import shelfdb.protocol as protocol
                assert set(protocol.__all__) <= set(dir(protocol))
                assert not hasattr(protocol, 'unknown_export')

                from shelfdb.protocol import Session, handle_client, serve, serve_unix
                from shelfdb.protocol.session import Session as ActualSession
                from shelfdb.protocol.server import (
                    handle_client as actual_handle_client,
                    serve as actual_serve,
                    serve_unix as actual_serve_unix,
                )
                assert Session is ActualSession
                assert handle_client is actual_handle_client
                assert serve is actual_serve
                assert serve_unix is actual_serve_unix
                assert protocol.serve is actual_serve
                assert protocol.__dict__['serve'] is actual_serve
                exports = {}
                exec('from shelfdb.protocol import *', exports)
                assert all(exports[name] is getattr(protocol, name)
                           for name in protocol.__all__)
            """),
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
