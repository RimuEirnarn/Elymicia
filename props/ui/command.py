import curses
from pathlib import Path
from shlex import split
from os import environ
from subprocess import call
from typing import Callable
from lymia.data import ReturnType, status
from lymia.forms import Text
from lymia.panel import Panel
from lymia.utils import hide_system
from props.files import change_dir
from props.state import WindowState

class Command:
    """Commands"""
    def __init__(self) -> None:
        self._buffer = Text("")
        self._cmd: dict[str, Callable[[curses.window, WindowState, list[str]], ReturnType]] = {}
        self._screen: curses.window
        self._state: WindowState
        self._helps: dict[str, str] = {}
        self._alias: dict[str, list[str]] = {}

    def add_command(self, *value: str, help: str = ""): # pylint: disable=redefined-builtin
        """Add command"""
        def inner(fn: Callable[[curses.window, WindowState, list[str]], ReturnType]):
            alias = ""
            for v in value:
                if self._cmd.get(v, None):
                    if fn != self._cmd[v]:
                        for aval in self._alias.copy().values():
                            if not v in aval:
                                continue
                            aval.remove(v)
                self._cmd[v] = fn
                if not self._alias.get(v, None):
                    alias = v
                    self._alias[alias] = []
                    self._helps[alias] = help
                else:
                    self._alias[alias].append(v)
            return fn
        return inner

    @property
    def alias(self):
        """Aliases"""
        return self._alias.copy()

    @property
    def helplist(self):
        """Help list"""
        return self._helps.copy()

    @property
    def cmds(self):
        """Commands"""
        return self._cmd.copy()

    def use_screen(self, screen: curses.window):
        """Give this class a screen!"""
        self._screen = screen

    def use_global_state(self, state: WindowState):
        """Use global state"""
        self._state = state

    @property
    def buffer(self):
        """buffer form"""
        return self._buffer

    def call(self) -> ReturnType:
        """Call appropriate function"""
        args = split(self._buffer.value)
        base = args[0] if len(args) >= 1 else ''
        fn = self._cmd.get(base, None)
        if not base:
            return ReturnType.CONTINUE
        if not fn:
            try:
                status.set(f"Command {base} is not found")
                return ReturnType.ERR
            except IndexError:
                return ReturnType.CONTINUE
        return fn(self._screen, self._state, args[1:])

def show_help(screen: curses.window, _):
    screen.box()
    for index, cmd in enumerate(command.cmds):
        hs = command.helplist[cmd]
        alias = command.alias.get(cmd, None)
        alias_str = ""
        if alias:
            alias_str = f" (Found alias: {' ,'.join(alias)}"
        screen.addstr(index + 1, 1, f"[{cmd}] -> {hs}{alias_str}")


command = Command()

@command.add_command("q")
def q(_, state: WindowState, *__):
    """Quit"""
    if state.popup:
        state.popup = None # type: ignore
        return ReturnType.CONTINUE
    return ReturnType.EXIT

@command.add_command("term", "terminal")
def term(screen: curses.window, *_):
    """Switch to terminal"""
    with hide_system(screen):
        ret = call(environ.get('SHELL', '/bin/sh'))
        input(f"\n[Return code {ret}] Press enter to return")
    return ReturnType.CONTINUE

@command.add_command("newtab", "nt")
def new_tab(_, state: WindowState, args: list[str]):
    """Open a new tab"""
    try:
        path = args[0]
        if path.startswith("\"") or path.startswith("'"):
            path = path[1:-1]
        state.start_files_view(path)
    except IndexError:
        status.set("Please provide the path")
    return ReturnType.CONTINUE

@command.add_command('closetab', 'ct')
def close_tab(_, state: WindowState, args: list[str]):
    """Close a tab by its index"""
    try:
        state.pop_files_view(int(args[0]))
    except TypeError:
        status.set(f"Invalid argument: {args[0]}")
        return ReturnType.ERR
    except IndexError:
        if len(args) > 1:
            status.set(f"Cannot find tab index {args[0]}, max is {len(state.panels) -1}")
            return ReturnType.ERR
        state.pop_files_view()
    if len(state.panels) == 0:
        return ReturnType.EXIT
    return ReturnType.CONTINUE

@command.add_command('t')
def t(_, s: WindowState, *__):
    """a"""
    status.set(f"Tabs: {len(s.tab_states)}:{len(s.panels)}")
    return ReturnType.CONTINUE

@command.add_command('pwd')
def pwd(_, state: WindowState, *__):
    """pwd"""
    status.set(f"{state.fetch()[1].cwd}")
    return ReturnType.CONTINUE

@command.add_command('cd')
def cd(_, state: WindowState, args: list[str]):
    """change dir"""
    try:
        path = Path(args[0]).expanduser().absolute()
    except IndexError:
        status.set("Please provide the path")
        return ReturnType.ERR
    tabstate = state.fetch()[1]
    ret = change_dir(tabstate, path, tabstate.menu.cursor)
    return ret

@command.add_command('help', help="Opens up help panel")
def help_(screen: curses.window, state: WindowState, _):
    maxy, maxx = screen.getmaxyx()
    panel = Panel(maxy - 2, maxx, 1, 0, show_help)
    state.popup = panel
    return ReturnType.CONTINUE

@command.add_command('close', help="Close any popup panel")
def closepanel(_, state: WindowState, __):
    state.popup = None # type: ignore
    return ReturnType.CONTINUE
