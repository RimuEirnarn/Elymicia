"""File manager"""

# pylint: disable=no-member,no-name-in-module

import curses
from os import getcwd
from os.path import basename
from curses import window
from lymia import Forms, HorizontalMenu, Menu, Panel, Scene, on_key, run
from lymia.data import ReturnType
from lymia.environment import Theme, Coloring
from lymia.colors import ColorPair, color

from props.ui.tabs import TabState, draw_tab
from props.utils import Directory


class Basic(Coloring):
    """Basic"""

    SELECTED = ColorPair(color.BLACK, color.YELLOW)
    DIRECTORY = ColorPair(color.GREEN, 0)
    SYMLINK = ColorPair(color.BLUE, 0)


def generate_file_view(path: str, size: tuple[int, int]):
    """Generate file manager view"""
    directory = Directory(path)
    state = TabState(
        path,
        Menu(directory, "", Basic.SELECTED, (1, 2), 1, count=lambda: len(directory)),
        directory,  # type: ignore
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
        self._menu.draw(self._screen)
        self.update_panels()
        self.show_status()

    def init(self, stdscr: window):
        super().init(stdscr)
        root_panel, root_state = generate_file_view(getcwd(), (self.height, self.width))
        p1, s1 = generate_file_view("/", (self.height, self.width))
        self._tabs = [root_panel, p1]
        self._tabs_state = [root_state, s1]
        self._menu = HorizontalMenu(
            lambda index: (basename(self._tabs_state[index].cwd) or "/", lambda: None),
            "[",
            "]",
            Basic.SELECTED,
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

    @on_key(curses.KEY_RIGHT)
    def fetch(self):
        """fetch"""
        _, cb = self._tabs_state[self._active].menu.fetch()
        if not isinstance(cb, Forms):
            cb()
        return ReturnType.CONTINUE


def init():
    """init"""
    env = Theme(0, Basic())
    return Root(), env


if __name__ == "__main__":
    run(init)
