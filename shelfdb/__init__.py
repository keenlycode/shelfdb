from .shelf import DB

def open(path):
    """Open database, return DB object.

    Args:
        path (string): directory path to database.

    Return:
        ``DB`` object.
    """
    return DB(path)
