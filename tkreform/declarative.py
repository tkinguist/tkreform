"""
TkReform declarative extension.

This extension provides a series of classes to support declarative style.

Example (Hello, World):
>>> import tkinter as tk
>>> import tkreform
>>> from tkreform.dec import W, Packer
>>> window = tkreform.Window(tk.Tk())
>>> window /= (
>>>     W(
>>>         tk.Frame, relief="ridge", borderwidth=2
>>>     ) * Packer(fill="both", expand=True) / (
>>>         W(tk.Label, text="Hello, World") * Packer(fill="x", expand=True),
>>>         W(tk.Button, text="Exit") * Packer(side="bottom")
>>>     ),
>>> )
>>> window[0][1].callback(window.destroy)
>>> window.loop()
"""

from dataclasses import dataclass
import sys
import tkinter as tk
from tkinter import ttk, Menu
from typing import TYPE_CHECKING, Any, Iterable, Optional, Type, Union

from tkreform.menu import MenuItem

if TYPE_CHECKING:
    from tkreform.base import Window

WidgetType = Union[tk.Widget, ttk.Widget]
WindowType = Union[tk.Tk, tk.Toplevel]

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

Direction = Literal["n", "ne", "e", "se", "s", "sw", "w", "nw"]
Compound = Literal["top", "left", "center", "right", "bottom", "none"]


@dataclass
class Gridder:
    column: Optional[int] = None
    columnspan: Optional[int] = None
    in_: Optional[Union[WidgetType, WindowType]] = None
    ipadx: Optional[int] = None
    ipady: Optional[int] = None
    padx: Optional[int] = None
    pady: Optional[int] = None
    row: Optional[int] = None
    rowspan: Optional[int] = None
    sticky: Optional[Direction] = None


@dataclass
class Packer:
    after: Optional[WidgetType] = None
    anchor: Optional[Literal[Direction, "center"]] = None
    before: Optional[WidgetType] = None
    expand: bool = False
    fill: Literal["none", "x", "y", "both"] = "none"
    in_: Optional[Union[WidgetType, WindowType]] = None
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
    in_: Optional[Union[WidgetType, WindowType]] = None
    bordermode: Optional[Literal["inside", "outside"]] = None
    anchor: Optional[Literal[Direction, "center"]] = None


@dataclass
class MenuBinder:
    win: Optional["Window"] = None


@dataclass
class NotebookAdder:
    state: Literal["normal", "disabled", "hidden"] = "normal"
    sticky: Optional[Direction] = None
    padding: ttk._Padding = (0, 0)
    text: str = ""
    image: Any = None
    compound: Compound = "none"
    underline: int = 0


class W:
    """Widget data pre-storage."""
    def __init__(self, widget: Type[WidgetType], **kwargs: Any) -> None:
        self.widget = widget
        self.kwargs = kwargs
        self.controller = None
        self.sub: Iterable[Union["W", MenuItem]] = ()

    def __mul__(self, other: Union[Gridder, Packer, Placer, MenuBinder, NotebookAdder]):
        self.controller = other
        return self

    def __truediv__(self, other: Iterable[Union["W", MenuItem]]):
        self.sub = other
        return self


class M(W):
    def __init__(self, it: MenuItem, **kwargs) -> None:
        super().__init__(Menu, **kwargs)
        self.it = it
