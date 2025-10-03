"""utils"""

from os import listdir, stat
from os.path import join
from stat import S_ISCHR, S_ISDOOR, S_ISDIR, S_ISBLK, S_ISLNK, S_ISFIFO, S_ISPORT, S_ISREG, S_ISSOCK, S_ISWHT
from typing import Any, TypedDict

from lymia import status
from lymia.menu import MenuEntry

DEFAULT = ('', 0)
class FormatColor(TypedDict):
    reg: tuple[str, int]
    link: tuple[str, int]
    directory: tuple[str, int]
    block: tuple[str, int]
    char: tuple[str, int]
    door: tuple[str, int]
    fifo: tuple[str, int]
    port: tuple[str, int]
    sock: tuple[str, int]
    whiteout: tuple[str, int]


def get_fmt(fmt: FormatColor, path: str):
    st = stat(path, follow_symlinks=False).st_mode
    if S_ISCHR(st):
        return fmt['char']
    if S_ISDOOR(st):
        return fmt['door']
    if S_ISDIR(st):
        return fmt['directory']
    if S_ISBLK(st):
        return fmt['block']
    if S_ISLNK(st):
        return fmt['link']
    if S_ISFIFO(st):
        return fmt['link']
    if S_ISPORT(st):
        return fmt['port']
    if S_ISREG(st):
        return fmt['reg']
    if S_ISSOCK(st):
        return fmt['sock']
    if S_ISWHT(st):
        return fmt['whiteout']
    return DEFAULT

def path_pointer(path: str, name: str, fmt: FormatColor):
    """Path pointer"""
    normalized = join(path, name)
    suffix, style = get_fmt(fmt, normalized)
    fname = name + suffix

    return MenuEntry(fname, lambda: status.set(normalized), style=style)

def _lsdir(path: str, fmt: FormatColor):
    """lsdir"""
    ls = listdir(path)
    ls.sort()
    return tuple(map(lambda a: path_pointer(path, a, fmt), ls))


class Directory:
    """lsdir"""
    def __init__(self, cwd: str, fmt: FormatColor) -> None:
        self._cwd = cwd
        self._c = _lsdir(cwd, fmt)
        self._fmt = fmt

    def __len__(self):
        return len(self._c)

    def refresh(self):
        """Refresh directory state"""
        self._c = _lsdir(self._cwd, self._fmt)

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
