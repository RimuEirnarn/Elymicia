from typing import Callable
from lymia.data import ReturnType
from lymia.forms import Text

class Command:
    """Commands"""
    def __init__(self) -> None:
        self._buffer = Text("")
        self._cmd: dict[str, Callable] = {}

    def add_command(self, value: str):
        """Add command"""
        def inner(fn: Callable[[], ReturnType]):
            self._cmd[value] = fn
            return fn
        return inner

    @property
    def buffer(self):
        """buffer form"""
        return self._buffer

    def call(self) -> ReturnType:
        """Call appropriate function"""
        fn = self._cmd.get(self._buffer.value, None)
        if not fn:
            return ReturnType.CONTINUE
        return fn()

command = Command()

@command.add_command("q")
def q():
    """Quit"""
    return ReturnType.EXIT
