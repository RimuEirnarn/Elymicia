"""Files operations"""
from os import environ, listdir
from os.path import join
from pathlib import Path
import curses
from subprocess import call

from lymia.data import ReturnType, status
from lymia.utils import hide_system
from props.state import WindowState
from props.ui.tabs import CursorHistory, TabState

def knock_knock(path: Path):
    """Return false if we aren't allowed"""
    try:
        listdir(path)
    except PermissionError:
        status.set("Cannot open: Permission Error")
        return False
    return True

def get_editor(state: WindowState):
    """Get file editor through environ"""
    app_ed = state.settings.get("EDITOR", "")
    sys_ed = environ.get('EDITOR', '')
    if sys_ed == '' and app_ed == '':
        raise ValueError("Please set an editor")
    return sys_ed or app_ed

def change_dir(state: TabState, path: Path, cursor: int = 0):
    """Change directory"""
    hist = CursorHistory(str(state.cwd), cursor)
    state.content.chdir(str(path))
    state.cwd = str(path)
    state.menu.reset_cursor()
    state.cursor_history.append(hist)
    return ReturnType.CONTINUE

def entry_file_manager(screen: curses.window, state: TabState, wstate: WindowState):
    """Change a tab's directory"""
    try:
        entry = state.menu.fetch()
        cursor = state.menu.cursor
    except IndexError:
        return ReturnType.CONTINUE

    path: Path = entry.content().expanduser()
    try:
        path.stat()
    except PermissionError:
        status.set(f"Access to: {path} failed, permission denied")
        return ReturnType.ERR

    if not path.is_dir() and not path.is_symlink():
        editor = get_editor(wstate)
        return open_file(screen, editor, str(path))
    if path.is_symlink():
        normalized = path.readlink()
        if str(normalized)[0] != "/":
            normalized = Path(join(state.cwd, str(normalized)))
        if not normalized.is_dir():
            editor = get_editor(wstate)
            return open_file(screen, editor, str(path))
    if not knock_knock(path):
        return ReturnType.ERR

    return change_dir(state, path, cursor)

def open_file(screen: curses.window, editor: str, file: str):
    """Open a file"""
    with hide_system(screen):
        call([editor, file])
    return ReturnType.CONTINUE
