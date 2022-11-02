"""
TkReform declarative extension.

This extension provides a series of classes to support declarative style.

Example (Hello, World):
>>> import tkinter as tk
>>> import tkreform
>>> from tkreform.dec import W, Packer
>>> window = tkreform.Window(tk.Tk())
>>> window /= (
>>>     W(tk.Frame, relief="ridge", borderwidth=2) * Packer(fill="both", expand=True) / (
>>>         W(tk.Label, text="Hello, World") * Packer(fill="x", expand=True),
>>>         W(tk.Button, text="Exit") * Packer(side="bottom")
>>>     ),
>>> )
>>> window[0][1].callback(window.destroy)
>>> window.loop()
"""

from dataclasses import dataclass
import sys
from tkinter import Tk, Toplevel, Widget, ttk
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
    in_: Optional[Union[Tk, Toplevel, Widget, ttk.Widget]] = None
    ipadx: Optional[int] = None
    ipady: Optional[int] = None
    padx: Optional[int] = None
    pady: Optional[int] = None
    row: Optional[int] = None
    rowspan: Optional[int] = None
    sticky: Optional[Literal[Direction, "nesw"]] = None


@dataclass
class Packer:
    after: Optional[Union[Widget, ttk.Widget]] = None
    anchor: Optional[Literal[Direction, "center"]] = None
    before: Optional[Union[Widget, ttk.Widget]] = None
    expand: bool = False
    fill: Literal["none", "x", "y", "both"] = "none"
    in_: Optional[Union[Tk, Toplevel, Widget, ttk.Widget]] = None
    ipadx: Optional[int] = None
    ipady: Optional[int] = None
    padx: Optional[int] = None
    pady: Optional[int] = None
    side: Optional[Literal["top", "bottom", "left", "right"]] = None


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
    in_: Optional[Union[Tk, Toplevel, Widget, ttk.Widget]] = None
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