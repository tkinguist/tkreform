from abc import ABCMeta, abstractmethod
import sys
import tkinter as tk
from tkinter import TclError, ttk

from tkreform.exceptions import MessageNotFound, WidgetNotArranged
from tkreform.linguist import Linguist
from tkreform.menu import MenuItem
from . import declarative as dec
from typing import (
    Any, Callable, Generic, Iterable, List, Optional, Tuple, Type, TypeVar, Union, cast,
    overload
)

# use Literal type
if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

# attempt to use PIL
try:
    from PIL.ImageTk import PhotoImage
    HAS_PIL = True
except ImportError:
    from tkinter import PhotoImage
    HAS_PIL = False

WidgetType = Union[tk.Widget, ttk.Widget]
WindowType = Union[tk.Tk, tk.Toplevel]
HasText = Union[tk.Label, tk.Button, ttk.Label, ttk.Button, tk.Message]

_T = TypeVar("_T", bound=Union[WidgetType, WindowType])
_WidgetT = TypeVar("_WidgetT", bound=WidgetType)
_WindowT = TypeVar("_WindowT", bound=WindowType)


class _Base(Generic[_T], metaclass=ABCMeta):
    def __init__(self, base: _T) -> None:
        """
        Base type of Window / Widget.

        - base: `WindowType | WidgetType` - base window / widget type
        """
        self.base = base
        self._sub_widget: List["Widget"] = []
        self._linguist: Optional[Linguist] = None

    @overload
    def __getitem__(self, it: int) -> "Widget":
        ...

    @overload
    def __getitem__(self, it: slice) -> List["Widget"]:
        ...

    def __getitem__(self, it: Union[int, slice]):
        return self._sub_widget[it]

    def __setitem__(self, it: int, val: "Widget"):
        self._sub_widget[it] = val

    def __iter__(self):
        return iter(self._sub_widget)

    def on(self, seq: str, append: bool = False):
        """
        Register response function on event sequence.

        - seq: `str` - event sequence
        - append: `bool` - decide to override or append function to target

        Returns: `Wrapper(func: (Event) -> Any)`

        Usage:
        >>> w = Window(...)  # or Widget(...)
        >>> @w.on("<Button-2>")
        ... def rclick(event: Event):
        ...     ...
        """
        def __wrapper(func: Callable[[tk.Event], Any]):
            self.base.bind(seq, func, append)
            return func
        return __wrapper

    def add_widget(self, sw: Type[_WidgetT], *args, **kwargs) -> "Widget[_WidgetT]":
        """
        Add a widget to window / widget.

        - sw: `Type[WidgetType]` - type of sub widget
        - *args, **kwargs - arguments for sub widget

        Returns: `Widget`
        """
        w = sw(self.base, *args, **kwargs)
        cw = Widget(w)
        self._sub_widget.append(cw)
        return cw

    def load_sub(self, sub: Iterable[Union[dec.W, MenuItem]]):
        """
        Load sub widgets recursively.

        - sub: `Iterable[dec.W]` - sub widget tree
        """
        for w in sub:
            if isinstance(w, MenuItem):
                self.base.add(w.type, **w.data)  # type: ignore
            else:
                _widget = self.add_widget(w.widget, **w.kwargs)
                _widget.linguist = self.linguist
                if isinstance(self.base, tk.Menu) and isinstance(w, dec.M):
                    self.base.add(w.it.type, menu=_widget.base, **w.it.data)
                elif isinstance(self.base, tk.PanedWindow):
                    self.base.add(_widget.base)
                elif isinstance(self.base, ttk.Notebook):
                    w.controller = cast(dec.NotebookAdder, w.controller)
                    self.base.add(
                        _widget.base,
                        **{k: getattr(w.controller, k) for k in w.controller.__dataclass_fields__}
                    )
                _widget.load_sub(w.sub)
                if w.controller is not None:
                    _widget.apply(w.controller)

    def __truediv__(self, other: Iterable[Union[dec.W, MenuItem]]):
        for old in self._sub_widget:
            old.destroy()
        self._sub_widget = []
        self.load_sub(other)
        return self

    def destroy(self):
        """Destroy window / widget."""
        self.base.destroy()

    @abstractmethod
    def update_translation(self):
        raise NotImplementedError

    @property
    def linguist(self):
        return self._linguist

    @linguist.setter
    def linguist(self, _l: Optional[Linguist]):
        self._linguist = _l
        self.update_translation()


class Widget(_Base, Generic[_WidgetT]):
    """
    Reformed Widget type based on `tkinter`.
    """
    base: _WidgetT

    def __init__(self, widget: _WidgetT) -> None:
        # To keep the content image alive, here gives a slot to add a
        # reference to the image so that the image wouldn't be recycled by GC
        # at the moment the image adder finishes its work.
        self._image_slot = None
        super().__init__(widget)
        self.base = widget
        if isinstance(widget, HasText):
            self._raw_text = self.text

    def grid(self, **kwargs):
        """
        Position a widget in the parent widget in a grid.

        - column: `int` - use cell identified with given column (starting
            with 0)
        - columnspan: `int` - this widget will span several columns
        - in_: `WindowType | WidgetType` - use master to contain this widget
        - ipadx: `int` - add internal padding in x direction
        - ipady: `int` - add internal padding in y direction
        - padx: `int` - add padding in x direction
        - pady: `int` - add padding in y direction
        - row: `int` - use cell identified with given row (starting with 0)
        - rowspan: `int` - this widget will span several rows
        - sticky: `str` - if cell is larger on which sides will this widget
            stick to the cell boundary
        """
        self.base.grid(**kwargs)

    def pack(self, **kwargs):
        """
        Pack a widget in the parent widget.

        - after: `WidgetType` - pack it after you have packed widget
        - anchor: `dec.Direction` - position widget according to given
            direction
        - before: `WidgetType` - pack it before you will pack widget
        - expand: `bool` - expand widget if parent size grows
        - fill: `Literal["none", "x", "y", "both"]` - fill widget if widget
            grows
        - in_: `WindowType | WidgetType` - use master to contain this widget
        - ipadx: `int` - add internal padding in x direction
        - ipady: `int` - add internal padding in y direction
        - padx: `int` - add padding in x direction
        - pady: `int` - add padding in y direction
        - side: `Literal["", "top", "bottom", "left", "right"]` - where to add
            this widget
        """
        self.base.pack(**kwargs)

    def place(self, **kwargs):
        """
        Place a widget in the parent widget.

        - in_: `WindowType | WidgetType` - master relative to which the widget
            is placed
        - x: `int` - locate anchor of this widget at position x of master
        - y: `int` - locate anchor of this widget at position y of master
        - relx: `int` - locate anchor of this widget between 0.0 and 1.0
            relative to width of master (1.0 is right edge)
        - rely: `int` - locate anchor of this widget between 0.0 and 1.0
            relative to height of master (1.0 is bottom edge)
        - anchor: `dec.Direction` - position anchor according to given
            direction
        - width: `int` - width of this widget in pixel
        - height: `int` - height of this widget in pixel
        - relwidth: `int` - width of this widget between 0.0 and 1.0 relative
            to width of master (1.0 is the same width as the master)
        - relheight: `int` - height of this widget between 0.0 and 1.0
            relative to height of master (1.0 is the same height as the
            master)
        - bordermode: `Literal["inside", "outside"]` - whether to take border
            width of master widget into account
        """
        self.base.place(**kwargs)

    def callback(self, func: Callable[[], Any]):
        """
        Set callback function.

        - func: `func: () -> Any` - the function to be called

        Usage:
        >>> w = Widget(...)
        >>> @w.callback
        ... def click():
        ...     ...
        """
        self.base["command"] = func
        return func

    command = callback

    def apply(
        self, geo: Union[dec.Gridder, dec.Packer, dec.Placer, dec.MenuBinder, dec.NotebookAdder]
    ):
        if isinstance(geo, dec.Gridder):
            self.grid(
                column=geo.column, columnspan=geo.columnspan,
                in_=geo.in_, ipadx=geo.ipadx, ipady=geo.ipady,
                padx=geo.padx, pady=geo.pady,
                row=geo.row, rowspan=geo.rowspan, sticky=geo.sticky
            )
        elif isinstance(geo, dec.Packer):
            self.pack(
                anchor=geo.anchor, expand=geo.expand, fill=geo.fill,
                in_=geo.in_, ipadx=geo.ipadx, ipady=geo.ipady,
                padx=geo.padx, pady=geo.pady, side=geo.side,
                after=geo.after, before=geo.before
            )
        elif isinstance(geo, dec.Placer):
            self.place(
                x=geo.x, y=geo.y, relx=geo.relx, rely=geo.rely,
                anchor=geo.anchor, width=geo.width, height=geo.height,
                relwidth=geo.relwidth, relheight=geo.relheight,
                bordermode=geo.bordermode, in_=geo.in_
            )
        elif isinstance(geo, dec.MenuBinder):
            if geo.win is not None:
                geo.win.menu = self.base
        elif isinstance(geo, dec.NotebookAdder):
            ...
        else:
            raise WidgetNotArranged(
                f"widget '{self.base}' has not been arranged by gridder, "
                "packer or placer."
            )

    def sync(self):
        if isinstance(self.base, tk.PanedWindow):
            for x in self._sub_widget:
                for k, v in self.base.paneconfigure(x.base).items():
                    try:
                        x.base.configure(**{k: v[-1]})
                    except TclError:
                        pass

    def __mul__(self, other: Union[dec.Gridder, dec.Packer, dec.Placer]):
        self.apply(other)
        return self

    def update_translation(self):
        if not self._sub_widget and hasattr(self, "_raw_text"):
            self.text = self._raw_text
        for w in self._sub_widget:
            w.linguist = self.linguist

    @property
    def text(self) -> str:
        """The text of the widget."""
        return self.base["text"]

    @text.setter
    def text(self, txt: str):
        self._raw_text = txt
        try:
            self.base["text"] = self._linguist[txt] if self._linguist else txt
        except MessageNotFound:
            pass

    @property
    def image(self) -> PhotoImage:  # type: ignore
        """The image of the widget."""
        return self.base["image"]

    @image.setter
    def image(self, img: Union[str, PhotoImage]):  # type: ignore
        _img = (PhotoImage(file=img) if isinstance(img, str) else img)
        self._image_slot = _img
        self.base["image"] = _img

    @property
    def width(self) -> int:
        """The width of the widget."""
        return self.base["width"]

    @width.setter
    def width(self, w: int):
        self.base["width"] = w

    @property
    def height(self) -> int:
        """The height of the widget."""
        return self.base["height"]

    @height.setter
    def height(self, h: int):
        self.base["height"] = h

    @property
    def size(self):
        """The size of the widget, in (x, y) form."""
        return self.width, self.height

    @size.setter
    def size(self, si: Tuple[int, int]):
        self.width, self.height = si

    @property
    def font(self) -> str:
        """The text font of the widget."""
        return self.base["font"]

    @font.setter
    def font(self, fon: Union[str, Tuple[str, int], Tuple[str, int, str]]):
        self.base["font"] = fon

    @property
    def disabled(self) -> bool:
        return self.base["state"] == "disabled"

    @disabled.setter
    def disabled(self, st: bool):
        self.base["state"] = "disabled" if st else "normal"


class Window(_Base, Generic[_WindowT]):
    """
    Reformed Window type based on `tkinter`.
    """
    base: _WindowT

    def __init__(self, base: _WindowT) -> None:
        """
        Initialize a new window.

        - base: `tk.Tk | tk.Toplevel` - base window type
        """
        super().__init__(base)
        self._raw_title = self.title

    def loop(self):
        """
        Run window mainloop.
        """
        self.base.mainloop()

    def sub_window(self):
        """
        Create a sub window.

        Returns: `tk.Toplevel`
        """
        sub = Window(tk.Toplevel(self.base))
        return sub

    def update(self):
        """Update window."""
        self.base.update()

    def wmhide(self):
        """Withdraw (hide) the window."""
        self.base.withdraw()

    withdraw = wmhide

    def minimize(self):
        """Minimize the window."""
        self.base.iconify()

    iconify = minimize

    def restore(self):
        """Restore the window from being withdrawn or minimized."""
        self.base.deiconify()

    deiconify = restore

    def on_protocol(self, protocol: str):
        """
        Register response function on protocol hook.

        - protocol: `str` - hook event

        Returns: `Wrapper(func: () -> Any)`

        Usage:
        >>> w = Window(...)
        >>> @w.on_protocol(...)
        ... def hook():
        ...     ...
        """
        def __wrapper(func: Callable[[], Any]):
            self.base.protocol(protocol, func)
            return func
        return __wrapper

    def update_translation(self):
        self.title = self._raw_title
        for w in self._sub_widget:
            w.linguist = self.linguist

    @property
    def title(self):
        """Window title."""
        return self.base.title()

    @title.setter
    def title(self, title: str):
        self._raw_title = title
        try:
            self.base.title(
                self._linguist[title] if self._linguist else title
            )
        except MessageNotFound:
            pass

    @property
    def geometry(self):
        """Geometry string."""
        return self.base.geometry()

    @geometry.setter
    def geometry(self, geo: str):
        self.base.geometry(geo)

    @property
    def xgeo(self):
        """
        A tuple (w, h, x, y) converted from geometry string
        """
        size, posx, posy = self.geometry.split("+", 2)
        sx, sy = (int(p) for p in size.split("x", 1))
        return sx, sy, int(posx), int(posy)

    @xgeo.setter
    def xgeo(self, xgeo: Tuple[int, int, int, int]):
        self.geometry = "{0}x{1}+{2}+{3}".format(*xgeo)

    @property
    def size(self):
        """Window size, in tuple (w, h)."""
        sx, sy, *_ = self.xgeo
        return sx, sy

    @size.setter
    def size(self, s: Tuple[int, int]):
        self.geometry = "{0}x{1}".format(*s)

    @property
    def pos(self):
        """Window position, in tuple (x, y)."""
        *_, px, py = self.xgeo
        return px, py

    @pos.setter
    def pos(self, p: Tuple[int, int]):
        self.geometry = "+{0}+{1}".format(*p)

    @property
    def icon(self):
        """Window icon."""
        return self.base.iconbitmap()

    @icon.setter
    def icon(self, ic: str):
        self.base.iconbitmap(ic, ic)

    def xicon(self, *ic: PhotoImage, inherit: bool = True):
        """
        Advanced icon setter.

        - *ic: `PhotoImage` - icon images
        - inherit: `bool` - whether the icon applies to sub windows
        """
        self.base.iconphoto(inherit, *ic)  # type: ignore

    @property
    def bgcolor(self) -> str:
        """Window background color."""
        return self.base["background"]

    @bgcolor.setter
    def bgcolor(self, bg: str):
        self.base["background"] = bg

    @property
    def resizable(self):
        """Window resizing ability in tuple (x, y)."""
        return self.base.resizable()

    @resizable.setter
    def resizable(self, resi: Union[bool, Tuple[bool, bool]]):
        resi = (resi, resi) if isinstance(resi, bool) else resi
        self.base.resizable(*resi)

    @property
    def size_range(self):
        """Resize range if window in ((xmin, xmax), (ymin, ymax))"""
        mx, my = self.base.minsize()
        nx, ny = self.base.maxsize()
        return (mx, nx), (my, ny)

    @size_range.setter
    def size_range(self, rng: Tuple[Tuple[int, int], Tuple[int, int]]):
        x, y = rng
        mx, nx = x
        my, ny = y
        self.base.minsize(mx, my)
        self.base.maxsize(nx, ny)

    @property
    def mode(self):
        """
        Window mode (state) in `Literal["normal", "iconic", "withdrawn"]`.
        """
        return self.base.state()

    @mode.setter
    def mode(self, mode: Literal["normal", "iconic", "withdrawn"]):
        self.base.state(mode)

    @property
    def alpha(self) -> float:
        """Window alpha."""
        return self.base.attributes("-alpha")

    @alpha.setter
    def alpha(self, a: float):
        self.base.attributes("-alpha", a)

    @property
    def top(self) -> bool:
        """Whether the window lies on the toppest."""
        return self.base.attributes("-topmost")

    @top.setter
    def top(self, t: bool):
        self.base.attributes("-topmost", t)

    @property
    def fullscreen(self) -> bool:
        """Whether the window occupies a whole screen."""
        return self.base.attributes("-fullscreen")

    @fullscreen.setter
    def fullscreen(self, f: bool):
        self.base.attributes("-fullscreen", f)

    @property
    def screenwh(self):
        """Current screen size in tuple (w, h)"""
        return self.base.winfo_screenwidth(), self.base.winfo_screenheight()

    @property
    def menu(self):
        return self.base["menu"]

    @menu.setter
    def menu(self, m):
        self.base["menu"] = m


class Application(Generic[_WindowT], metaclass=ABCMeta):
    def __init__(self, base: Union[_WindowT, Window[_WindowT]]) -> None:
        self.win = base if isinstance(base, Window) else Window(base)
        self.setup()

    @abstractmethod
    def setup(self) -> None:
        raise NotImplementedError