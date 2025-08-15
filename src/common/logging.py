import sys
from typing import Any

# ANSI escape codes for colors
ANSI_COLORS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "blue": "\033[34m",
    "orange": "\033[38;5;208m",  # Extended 256-color orange
    "yellow": "\033[33m",
}
RESET = "\033[0m"


def print_color(color: str, *objects: Any, sep: str = ' ', end: str = '\n', file=None, flush: bool = False) -> None:
    """Generic color printer."""
    if file is None:
        file = sys.stdout
    color_code = ANSI_COLORS.get(color.lower(), "")
    text = sep.join(str(obj) for obj in objects)
    print(f"{color_code}{text}{RESET}", end=end, file=file, flush=flush)


# Wrappers for convenience
def print_red(*objects: Any, **kwargs) -> None:
    print_color("red", *objects, **kwargs)


def print_green(*objects: Any, **kwargs) -> None:
    print_color("green", *objects, **kwargs)


def print_blue(*objects: Any, **kwargs) -> None:
    print_color("blue", *objects, **kwargs)


def print_orange(*objects: Any, **kwargs) -> None:
    print_color("orange", *objects, **kwargs)


def print_yellow(*objects: Any, **kwargs) -> None:
    print_color("yellow", *objects, **kwargs)
