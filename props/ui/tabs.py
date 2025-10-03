"""Tabs"""

# pylint: disable=no-member

import curses
from dataclasses import dataclass

from lymia import Menu
from ..utils import Directory

@dataclass
class TabState:
    """Tab state"""
    cwd: str
    menu: Menu[str]
    content: Directory

def draw_tab(screen: curses.window, state: TabState):
    """Draw tab"""
    screen.erase()
    screen.box()
    state.menu.draw(screen)
