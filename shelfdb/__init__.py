from .shelf import DB

def open(path: str) -> 'shelfdb.DB':
    """Open database, return `shelfdb.DB` object.

    :param `path (str)`: database's directory path.
    """
    return DB(path)
