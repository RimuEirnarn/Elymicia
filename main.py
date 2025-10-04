"""File manager"""

# pylint: disable=no-member,no-name-in-module

import curses
from os import getcwd, listdir
from os.path import basename, join
from curses import window
from pathlib import Path
from lymia import HorizontalMenu, Menu, Panel, Scene, on_key, run
from lymia.data import ReturnType, status
from lymia.environment import Theme, Coloring
from lymia.colors import ColorPair, color

from props.ui.tabs import TabState, draw_tab, CursorHistory
from props.utils import Directory, FormatColor, DEFAULT as FMT_DFT


class Basic(Coloring):
    """Basic"""

    SELECTED = ColorPair(color.BLACK, color.YELLOW)
    DIRECTORY = ColorPair(color.BLUE, 0)
    SYMLINK = ColorPair(color.CYAN, 0)
    DEVICE = ColorPair(color.YELLOW, 0)
    SOCK = ColorPair(color.GREEN, 0)
    BLOCK = ColorPair(color.YELLOW, 0)

basic = Basic()

fmt: FormatColor = {
    'reg': FMT_DFT,
    "block": ("", int(Basic.BLOCK)),
    "char": ("", int(Basic.DEVICE)),
    "directory": ("/", int(Basic.DIRECTORY)),
    "door": FMT_DFT,
    "fifo": FMT_DFT,
    "link": ('@', int(Basic.SYMLINK)),
    "port": FMT_DFT,
    "sock": ("", int(Basic.SOCK)),
    "whiteout": FMT_DFT
} # type: ignore

def knock_knock(path: Path):
    """Return false if we aren't allowed"""
    try:
        listdir(path)
    except PermissionError:
        status.set("Cannot open: Permission Error")
        return False
    return True

def generate_file_view(path: str, size: tuple[int, int]):
    """Generate file manager view"""
    directory = Directory(path, fmt)
    state = TabState(
        path,
        Menu(directory, "", "", Basic.SELECTED, (1, 2), 1, count=lambda: len(directory)), # type: ignore
        directory,  # type: ignore,
        []
    )
    panel = Panel(size[0] - 2, size[1], 1, 0, draw_tab, state)
    return panel, state


class Root(Scene):
    """Root scene"""

    def __init__(self) -> None:
        self._tabs: list[Panel]
        self._tabs_state: list[TabState]
        self._menu: HorizontalMenu
        self._active = 0
        self._targets = []
        super().__init__()

    def update_panels(self):
        for panel in self._tabs:
            panel.draw()

    def draw(self):
        self.update_panels()
        self._menu.draw(self._screen)
        self.show_status()

    def init(self, stdscr: window):
        super().init(stdscr)
        root_panel, root_state = generate_file_view(getcwd(), (self.height, self.width))
        p1, s1 = generate_file_view("/", (self.height, self.width))
        p2, s2 = generate_file_view("/home", (self.height, self.width))
        p3, s3 = generate_file_view("/dev", (self.height, self.width))
        self._tabs = [root_panel, p1, p2, p3]
        self._tabs_state = [root_state, s1, s2, s3]
        self._menu = HorizontalMenu(
            lambda index: (basename(self._tabs_state[index].cwd) or "/", lambda: None),
            "[",
            suffix="]",
            selected_style=Basic.SELECTED,
        )
        self.tab_visibility_refresh()

    def tab_visibility_refresh(self):
        """Refresh tab visibility"""
        for index, tab in enumerate(self._tabs):
            if index != self._active:
                tab.hide()
                self.cleanup_menu_keymap()
            if index == self._active:
                tab.show()
                self.register_keymap(self._tabs_state[self._active].menu)

    def _fetch(self, index: int | None = None) -> tuple[Panel, TabState]:
        if index is None:
            index = self._active
        return self._tabs[index], self._tabs_state[index]


    @on_key("q")
    def quit(self):
        """quit"""
        return ReturnType.EXIT

    @on_key("\t")
    def switch(self):
        """switch"""
        cursor = self._menu._cursor  # pylint: disable=protected-access
        if cursor == len(self._tabs_state) - 1:
            self._menu._cursor = 0  # pylint: disable=protected-access
            cursor = 0
            self._active = cursor
            self.tab_visibility_refresh()
            return ReturnType.CONTINUE
        self._menu.move_down()
        cursor += 1
        self._active = cursor
        self.tab_visibility_refresh()
        return ReturnType.CONTINUE

    @on_key(curses.KEY_LEFT)
    def back(self):
        """back"""
        _, state_active = self._fetch()
        path = Path(state_active.cwd)
        parent = str(path.parent)

        try:
            ps = state_active.cursor_history.pop()
        except IndexError:
            ps = CursorHistory(parent, 0)

        state_active.cwd = str(ps.path)
        state_active.content.chdir(ps.path)
        state_active.menu.seek(ps.cursor)
        status.set(repr(state_active.cursor_history))
        return ReturnType.CONTINUE


    @on_key(curses.KEY_RIGHT)
    def fetch(self):
        """fetch"""
        _, state_active = self._fetch()
        try:
            entry = state_active.menu.fetch()
            cursor = state_active.menu.cursor
        except IndexError:
            return ReturnType.CONTINUE
        if not callable(entry.content):
            return ReturnType.CONTINUE

        file: Path = entry.content() # type: ignore
        if not file.is_dir() and not file.is_symlink():
            status.set(str(file))
            return ReturnType.CONTINUE
        if file.is_symlink():
            normalized = file.readlink()
            if str(normalized)[0] != '/':
                normalized = Path(join(state_active.cwd, str(normalized)))
            if not normalized.is_dir():
                status.set(str(file))
                return ReturnType.CONTINUE
            status.set(f"{file} -> {normalized}")
        if not knock_knock(file):
            return ReturnType.CONTINUE
        hist = CursorHistory(str(state_active.cwd), cursor)
        state_active.content.chdir(str(file))
        state_active.cwd = str(file)
        state_active.menu.reset_cursor()
        state_active.cursor_history.append(hist)
        status.set(repr(state_active.cursor_history))
        return ReturnType.CONTINUE


def init():
    """init"""
    env = Theme(0, basic)
    return Root(), env


if __name__ == "__main__":
    run(init)
