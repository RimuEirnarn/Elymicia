"""File manager"""

# pylint: disable=no-member,no-name-in-module

import curses
from os import getcwd
from curses import window
from pathlib import Path
from lymia import HorizontalMenu, Scene, on_key, run
from lymia.data import ReturnType, status
from lymia.environment import Theme

from props.files import entry_change_dir
from props.state import WindowState
from props.colors import basic, Basic
from props.ui.command import command
from props.ui.tabs import CursorHistory


class Root(Scene):
    """Root scene"""

    def __init__(self) -> None:
        self._state = WindowState()
        self._menu: HorizontalMenu
        self._active_cursor = 0
        super().__init__()

    @property
    def size(self):
        """size"""
        return (self.height, self.width)

    def update_panels(self):
        for panel in self._state.panels:
            panel.draw()

    def draw(self):
        self.update_panels()
        self._menu.draw(self._screen)
        self.show_status()

    def deferred_op(self):
        if command.buffer.editing:
            command.buffer.reposition_cursor(self._screen, 1)

    def init(self, stdscr: window):
        super().init(stdscr)
        self._state.winsize = self.size
        command.use_screen(stdscr)
        command.use_global_state(self._state)
        self._state.start_files_view(getcwd(), self.size)
        self._state.start_files_view("/", self.size)
        self._state.start_files_view("/home", self.size)
        self._state.start_files_view("/dev", self.size)
        self._menu = HorizontalMenu(
        self._state.tab_views,
            "[",
            suffix="]",
            selected_style=Basic.SELECTED,
        )
        self._state.trig_active(self._menu.seek)
        self._state.trig_active(lambda _: self.tab_visibility_refresh())
        self._state.active = 0
        self.tab_visibility_refresh()

    def tab_visibility_refresh(self):
        """Refresh tab visibility"""
        for index, tab in enumerate(self._state.panels):
            if index != self._state.active:
                tab.hide()
                self.cleanup_menu_keymap()
            if index == self._state.active:
                tab.show()
                self.register_keymap(self._state.fetch()[1].menu)

    def keymap_override(self, key: int) -> ReturnType:
        if command.buffer.editing:
            ret = command.buffer.handle_edit(key)
            if ret == ReturnType.REVERT_OVERRIDE:
                self._override = False
                return self.on_exitcmd()
            status.set(f':{command.buffer.displayed_value}')
            return ret
        return ReturnType.REVERT_OVERRIDE

    def on_exitcmd(self):
        """a"""
        status.set("")
        ret = command.call()
        command.buffer.exit_edit()
        command.buffer.value = '' # type: ignore
        return ret

    def select_menu_item(self):
        """Select menu item"""
        command.buffer.enter_edit()
        self._override = True
        status.set(":")
        command.buffer.set_field_pos(self.height - 1)
        return ReturnType.OVERRIDE

    @on_key(":")
    def enter_command(self):
        """a"""
        return self.select_menu_item()

    @on_key("\t")
    def switch(self):
        """switch"""
        cursor = self._menu._cursor  # pylint: disable=protected-access
        if self._state.switch_files_view(cursor) == 'first':
            self._menu._cursor = 0  # pylint: disable=protected-access
            self.tab_visibility_refresh()
            return ReturnType.CONTINUE
        self._menu.move_down()
        self.tab_visibility_refresh()
        return ReturnType.CONTINUE

    @on_key(curses.KEY_RESIZE)
    def on_resize(self):
        """On resize"""
        self._state.winsize = self.size
        return ReturnType.CONTINUE

    @on_key(curses.KEY_LEFT)
    def back(self):
        """back"""
        _, state_active = self._state.fetch()
        path = Path(state_active.cwd)
        parent = str(path.parent)

        try:
            ps = state_active.cursor_history.pop()
        except IndexError:
            ps = CursorHistory(parent, 0)
            if parent == "/" and str(path) == "/":
                return ReturnType.CONTINUE

        state_active.cwd = str(ps.path)
        state_active.content.chdir(ps.path)
        state_active.menu.seek(ps.cursor)
        return ReturnType.CONTINUE

    @on_key(curses.KEY_RIGHT)
    def fetch(self):
        """fetch"""
        return entry_change_dir(self._state.fetch()[1])


def init():
    """init"""
    env = Theme(0, basic)
    return Root(), env


if __name__ == "__main__":
    run(init)
