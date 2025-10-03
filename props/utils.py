"""utils"""

from os import listdir
from os.path import join, isdir, islink
from typing import Any

from lymia import status



def path_pointer(path: str, name: str):
    """Path pointer"""
    fname = name
    normalized = join(path, name)
    if isdir(normalized):
        fname += "/"
    elif islink(normalized):
        fname += "@"

    return fname, lambda: status.set(normalized)

def _lsdir(path: str):
    """lsdir"""
    ls = listdir(path)
    return tuple(map(lambda a: path_pointer(path, a), ls))


class Directory:
    """lsdir"""
    def __init__(self, cwd: str) -> None:
        self._cwd = cwd
        self._c = _lsdir(cwd)

    def __len__(self):
        return len(self._c)

    def refresh(self):
        """Refresh directory state"""
        self._c = _lsdir(self._cwd)

    def __call__(self, index: int):
        return self._c[index] # type: ignore

    def __iter__(self):
        return self._c.__iter__()

class Mapper:
    """Map an object to whatever"""
    def __init__(self, content: Any) -> None:
        self._content = content

    def __call__(self, index: int) -> Any:
        return self._content[index]

    def __iter__(self):
        return iter(self._content)
