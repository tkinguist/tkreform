from dataclasses import dataclass
import sys
from tkinter import Widget
from typing import Any, Iterable, Type, Union

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

Direction = Literal["n", "ne", "e", "se", "s", "sw", "w", "nw"]


@dataclass
class Gridder:
    column: int = 0
    columnspan: int = 1
    ipadx: int = 0
    ipady: int = 0
    padx: int = 0
    pady: int = 0
    row: int = 0
    rowspan: int = 1
    sticky: Literal[Direction, "nesw"] = "nesw"


@dataclass
class Packer:
    anchor: Literal[Direction, "center"] = "center"
    expand: bool = False
    fill: Literal["none", "x", "y", "both"] = "none"
    ipadx: int = 0
    ipady: int = 0
    padx: int = 0
    pady: int = 0
    side: Literal["", "top", "bottom", "left", "right"] = ""


class W:
    def __init__(self, widget: Type[Widget], **kwargs: Any) -> None:
        self.widget = widget
        self.kwargs = kwargs
        self.controller = None
        self.sub: Iterable["W"] = ()

    def __mul__(self, other: Union[Gridder, Packer]):
        self.controller = other
        return self

    def __truediv__(self, other: Iterable["W"]):
        self.sub = other
        return self