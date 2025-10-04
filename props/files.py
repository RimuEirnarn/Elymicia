from os import listdir
from os.path import join
from pathlib import Path
from lymia.data import ReturnType, status
from props.ui.tabs import CursorHistory, TabState

def knock_knock(path: Path):
    """Return false if we aren't allowed"""
    try:
        listdir(path)
    except PermissionError:
        status.set("Cannot open: Permission Error")
        return False
    return True

def change_dir(state: TabState, path: Path, cursor: int = 0):
    """Change directory"""
    if not path.is_dir() and not path.is_symlink():
        status.set(str(path))
        return ReturnType.ERR
    if path.is_symlink():
        normalized = path.readlink()
        if str(normalized)[0] != "/":
            normalized = Path(join(state.cwd, str(normalized)))
        if not normalized.is_dir():
            status.set(str(path))
            return ReturnType.ERR
        status.set(f"{path} -> {normalized}")
    if not knock_knock(path):
        return ReturnType.ERR

    hist = CursorHistory(str(state.cwd), cursor)
    state.content.chdir(str(path))
    state.cwd = str(path)
    state.menu.reset_cursor()
    state.cursor_history.append(hist)
    return ReturnType.CONTINUE

def entry_change_dir(state: TabState):
    """Change a tab's directory"""
    try:
        entry = state.menu.fetch()
        cursor = state.menu.cursor
    except IndexError:
        return ReturnType.CONTINUE

    file: Path = entry.content()
    try:
        file.stat()
    except PermissionError:
        status.set(f"Access to: {file} failed, permission denied")
        return ReturnType.ERR

    return change_dir(state, file, cursor)
