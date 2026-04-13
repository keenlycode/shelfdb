from .client import connect_async as connect_async
from .shelf import DB


def open(path: str) -> DB:
    """Open database, return `shelfdb.DB` object.

    :param `path (str)`: database's directory path.
    """
    return DB(path)
