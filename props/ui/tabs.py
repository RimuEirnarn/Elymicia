"""Tabs"""

# pylint: disable=no-member

import curses
from dataclasses import dataclass
from typing import NamedTuple

from lymia import Menu
from ..utils import Directory

class CursorHistory(NamedTuple):
    path: str
    cursor: int

@dataclass
class TabState:
    """Tab state"""
    cwd: str
    menu: Menu[str]
    content: Directory
    cursor_history: list[CursorHistory]

def draw_tab(screen: curses.window, state: TabState):
    """Draw tab"""
    screen.erase()
    screen.box()
    state.menu.draw(screen)
