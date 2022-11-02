from dataclasses import dataclass
import sys
from tkinter import Widget
from typing import Any, Iterable, Optional, Type, Union

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

Direction = Literal["n", "ne", "e", "se", "s", "sw", "w", "nw"]


@dataclass
class Gridder:
    column: Optional[int] = None
    columnspan: Optional[int] = None
    ipadx: Optional[int] = None
    ipady: Optional[int] = None
    padx: Optional[int] = None
    pady: Optional[int] = None
    row: Optional[int] = None
    rowspan: Optional[int] = None
    sticky: Literal[Direction, "nesw"] = "nesw"


@dataclass
class Packer:
    anchor: Literal[Direction, "center"] = "center"
    expand: bool = False
    fill: Literal["none", "x", "y", "both"] = "none"
    ipadx: Optional[int] = None
    ipady: Optional[int] = None
    padx: Optional[int] = None
    pady: Optional[int] = None
    side: Literal["", "top", "bottom", "left", "right"] = ""


@dataclass
class Placer:
    x: Optional[int] = None
    y: Optional[int] = None
    relx: Optional[int] = None
    rely: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    relwidth: Optional[int] = None
    relheight: Optional[int] = None
    bordermode: Optional[Literal["inside", "outside"]] = None
    anchor: Optional[Literal[Direction, "center"]] = None


class W:
    """Widget data pre-storage."""
    def __init__(self, widget: Type[Widget], **kwargs: Any) -> None:
        self.widget = widget
        self.kwargs = kwargs
        self.controller = None
        self.sub: Iterable["W"] = ()

    def __mul__(self, other: Union[Gridder, Packer, Placer]):
        self.controller = other
        return self

    def __truediv__(self, other: Iterable["W"]):
        self.sub = other
        return self