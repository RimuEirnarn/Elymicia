"""Global Window State"""
from pathlib import Path
from posixpath import basename
from typing import Callable
from lymia.data import status
from lymia.panel import Panel
from lymia.menu import  Menu
from props.ui.tabs import TabState, draw_tab
from props.utils import Directory

from .colors import fmt, Basic

class WindowState:
    """Window state to manage panels and tab states"""

    def __init__(self):
        self._panels: list[Panel] = []
        self._tab_states: list[TabState] = []
        self._winsize = (0, 0)
        self._trig: list[Callable[[int], None]] = []
        self._active = 0
        self._popup: list[Panel] = []
        self._kv: dict[str, str] = {}

    @property
    def settings(self):
        """Returns app setting (volatile!)"""
        return self._kv

    @property
    def popup(self):
        """Popup panel"""
        return self._popup

    def reset_popup(self):
        """Reset popup to None"""
        self._popup.clear()

    @property
    def winsize(self):
        """Window size"""
        return self._winsize

    @winsize.setter
    def winsize(self, value: tuple[int, int]):
        """Window size"""
        self._winsize = value

    @property
    def tabs(self):
        """tabs"""
        return self._panels

    @property
    def panels(self):
        """panels"""
        return self._panels

    @property
    def tab_states(self):
        """Tab states"""
        return self._tab_states

    @property
    def active(self):
        """Return the active tab's index"""
        return self._active

    @active.setter
    def active(self, value: int):
        """Return the active tab's index"""
        if value > len(self.tab_states) - 1:
            return
        if value < 0:
            return
        self._active = value

        for trig in self._trig:
            trig(value)

    def trig_active(self, fn: Callable[[int], None]):
        """Push notification for active's state changes"""
        self._trig.append(fn)

    def fetch(self, index: int | None = None):
        """Fetch panel and its state by the index"""
        if index is None:
            index = self._active

        return self.panels[index], self.tab_states[index]

    def tab_views(self, index: int):
        """Return tab views"""
        return basename(self.tab_states[index].cwd) or '/', lambda: None

    def start_files_view(self, path: str, size: tuple[int, int] = (-1, -1)):
        """Generate file manager view"""
        if size == (-1, -1):
            size = self.winsize
        path = str(Path(path).expanduser())
        try:
            directory = Directory(path, fmt)
        except (FileNotFoundError, PermissionError) as exc:
            status.set(f"{type(exc).__name__}: {str(exc)}")
            return 0, 0
        state = TabState(
            path,
            Menu(directory, "", "",  # type: ignore
                 Basic.SELECTED, (1, 2), 1, count=lambda: len(directory)),
            directory,  # type: ignore,
            [],
        )
        panel = Panel(size[0] - 2, size[1], 1, 0, draw_tab, state)
        self.panels.append(panel)
        self.tab_states.append(state)
        self.active = len(self.tab_states) - 1
        return panel, state

    def pop_files_view(self, index: int | None = None):
        """Pop files view"""
        pop_index = 0
        if index is None:
            pop_index = -1
            index = len(self._panels) - 2
        else:
            pop_index = index
        self._panels.pop(pop_index)
        self._tab_states.pop(pop_index)
        self.active = index

    def switch_files_view(self, index: int):
        """Switch file view"""
        if index >= len(self.tab_states) - 1:
            self._active = 0
            return 'first'
        self._active += 1
        return 'right'
