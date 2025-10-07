from lymia.colors import ColorPair, Coloring, color
from props.utils import FormatColor, DEFAULT as FMT_DFT


class Basic(Coloring):
    """Basic"""

    SELECTED = ColorPair(color.BLACK, color.YELLOW)
    DIRECTORY = ColorPair(color.BLUE, -1)
    SYMLINK = ColorPair(color.CYAN, -1)
    DEVICE = ColorPair(color.YELLOW, color.BLACK)
    SOCK = ColorPair(color.GREEN, -1)
    BLOCK = ColorPair(color.YELLOW, -1)


basic = Basic()

fmt: FormatColor = {
    "reg": FMT_DFT,
    "block": ("", int(Basic.BLOCK)),
    "char": ("", int(Basic.DEVICE)),
    "directory": ("/", int(Basic.DIRECTORY)),
    "door": FMT_DFT,
    "fifo": FMT_DFT,
    "link": ("@", int(Basic.SYMLINK)),
    "port": FMT_DFT,
    "sock": ("", int(Basic.SOCK)),
    "whiteout": FMT_DFT,
}  # type: ignore
