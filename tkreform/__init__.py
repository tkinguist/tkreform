import sys
import tkinter as tk
from tkinter import ttk

from tkreform.exceptions import WidgetNotArranged
from . import declarative as dec
from typing import Any, Callable, Iterable, List, Tuple, Type, Union

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

try:
    from PIL.Image import Image  # type: ignore
    from PIL.ImageTk import PhotoImage  # type: ignore
    HAS_PIL = True
except ImportError:
    Image = tk.Image
    PhotoImage = tk.PhotoImage
    HAS_PIL = False

WidgetType = Union[tk.Widget, ttk.Widget]
WindowType = Union[tk.Tk, tk.Toplevel]


class Base:
    def __init__(self, base: Union[WindowType, WidgetType]) -> None:
        self.base = base
        self.__declarative_prev_widget = None
        self._sub_widget: List["Widget"] = []

    def __getitem__(self, it: int):
        return self._sub_widget[it]

    def on(self, seq: str, append: bool = False):
        def __wrapper(func: Callable[[tk.Event], Any]):
            self.base.bind(seq, func, append)
        return __wrapper

    def add_widget(self, sw: Type[WidgetType], *args, **kwargs):
        w = sw(self.base, *args, **kwargs)
        return Widget(w)

    def load_sub(self, sub: Iterable[dec.W]):
        for w in sub:
            _widget = self.add_widget(w.widget, **w.kwargs)
            _widget.load_sub(w.sub)
            ctl = w.controller
            if isinstance(ctl, dec.Gridder):
                _widget.grid(
                    column=ctl.column, columnspan=ctl.columnspan,
                    ipadx=ctl.ipadx, ipady=ctl.ipady,
                    padx=ctl.padx, pady=ctl.pady,
                    row=ctl.row, rowspan=ctl.rowspan, sticky=ctl.sticky
                )
            elif isinstance(ctl, dec.Packer):
                _widget.pack(
                    anchor=ctl.anchor, expand=ctl.expand, fill=ctl.fill,
                    ipadx=ctl.ipadx, ipady=ctl.ipady,
                    padx=ctl.padx, pady=ctl.pady, side=ctl.side,
                    **(
                        dict()
                            if self.__declarative_prev_widget is None else
                        dict(after=self.__declarative_prev_widget.base)
                    )
                )
            else:
                raise WidgetNotArranged(f"widget '{_widget.base}' has not been arranged by gridder or packer.")
            self._sub_widget.append(_widget)
            self.__declarative_prev_widget = _widget

    def destroy(self):
        self.base.destroy()


class Widget(Base):
    base: WidgetType

    def __init__(self, widget: WidgetType) -> None:
        # To keep the content image alive, here gives a slot to add a
        # reference to the image so that the image wouldn't be recycled by GC
        # at the moment the image adder finishes its work.
        self._image_slot = None
        super().__init__(widget)

    def grid(self, *args, **kwargs):
        self.base.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.base.pack(*args, **kwargs)

    def callback(self, func: Callable[[], Any]):
        self.base["command"] = func
        return func

    @property
    def text(self) -> str:
        return self.base["text"]

    @text.setter
    def text(self, txt: str):
        self.base["text"] = txt

    @property
    def image(self) -> PhotoImage:  # type: ignore
        return self.base["image"]

    @image.setter
    def image(self, img: Union[str, Image, PhotoImage]):  # type: ignore
        _img = (
            PhotoImage(file=img)
                if isinstance(img, str) else
            PhotoImage(img)  # type: ignore
                if isinstance(img, Image) and HAS_PIL else
            img
        )
        self._image_slot = _img
        self.base["image"] = _img

    @property
    def width(self) -> int:
        return self.base["width"]

    @width.setter
    def width(self, w: int):
        self.base["width"] = w

    @property
    def height(self) -> int:
        return self.base["height"]

    @height.setter
    def height(self, h: int):
        self.base["height"] = h

    @property
    def size(self):
        return self.width, self.height

    @size.setter
    def size(self, si: Tuple[int, int]):
        self.width, self.height = si

    @property
    def font(self) -> str:
        return self.base["font"]

    @font.setter
    def font(self, fon: Union[str, Tuple[str, int], Tuple[str, int, str]]):
        self.base["font"] = fon


class Window(Base):
    """
    Reformed Window type based on `tkinter`.
    """
    base: WindowType

    def __init__(self, base: WindowType) -> None:
        """
        Initialize a new window.  
        
        Args:
        - base: `tk.Tk | tk.Toplevel` - base window type
        """
        super().__init__(base)

    def loop(self):
        """
        Run window mainloop.
        """
        self.base.mainloop()

    def sub_window(self):
        sub = type(self)(tk.Toplevel(self.base))
        return sub

    def close(self):
        self.base.destroy()

    def update(self):
        self.base.update()

    def wmhide(self):
        self.base.withdraw()

    def minimize(self):
        self.base.iconify()

    def restore(self):
        self.base.deiconify()
    
    def on_protocol(self, protocol: str):
        def __wrapper(func: Callable[[], Any]):
            self.base.protocol(protocol, func)
            return func
        return __wrapper

    def __truediv__(self, other: Iterable[dec.W]):
        for old in self._sub_widget:
            old.destroy()
        super().load_sub(other)
        return self

    @property
    def title(self):
        return self.base.title()

    @title.setter
    def title(self, title: str):
        self.base.title(title)

    @property
    def geometry(self):
        return self.base.geometry()

    @geometry.setter
    def geometry(self, geo: str):
        self.base.geometry(geo)

    @property
    def xgeo(self):
        """
        A tuple converted from geometry string
        """
        size, posx, posy = self.geometry.split("+", 2)
        sx, sy = (int(p) for p in size.split("x", 1))
        return sx, sy, int(posx), int(posy)

    @xgeo.setter
    def xgeo(self, xgeo: Tuple[int, int, int, int]):
        self.geometry = "{0}x{1}+{2}+{3}".format(*xgeo)

    @property
    def size(self):
        sx, sy, *_ = self.xgeo
        return sx, sy

    @size.setter
    def size(self, s: Tuple[int, int]):
        self.geometry = "{0}x{1}".format(*s)

    @property
    def pos(self):
        *_, px, py = self.xgeo
        return px, py

    @pos.setter
    def pos(self, p: Tuple[int, int]):
        self.geometry = "+{0}+{1}".format(*p)

    @property
    def icon(self):
        return self.base.iconbitmap()

    @icon.setter
    def icon(self, ic: str):
        self.base.iconbitmap(ic, ic)

    def xicon(self, *ic: PhotoImage, inherit: bool = True):  # type: ignore
        self.base.iconphoto(inherit, *ic)

    @property
    def bgcolor(self) -> str:
        return self.base["background"]

    @bgcolor.setter
    def bgcolor(self, bg: str):
        self.base["background"] = bg

    @property
    def resizable(self):
        return self.base.resizable()

    @resizable.setter
    def resizable(self, resi: Union[bool, Tuple[bool, bool]]):
        resi = (resi, resi) if isinstance(resi, bool) else resi
        self.base.resizable(*resi)

    @property
    def size_range(self):
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
        return self.base.state()

    @mode.setter
    def mode(self, mode: Literal["normal", "iconic", "withdrawn"]):
        self.base.state(mode)

    @property
    def alpha(self) -> float:
        return self.base.attributes("-alpha")

    @alpha.setter
    def alpha(self, a: float):
        self.base.attributes("-alpha", a)

    @property
    def top(self) -> bool:
        return self.base.attributes("-topmost")

    @top.setter
    def top(self, t: bool):
        self.base.attributes("-topmost", t)

    @property
    def fullscreen(self) -> bool:
        return self.base.attributes("-fullscreen")

    @fullscreen.setter
    def fullscreen(self, f: bool):
        self.base.attributes("-fullscreen", f)

    @property
    def screenwh(self):
        return self.base.winfo_screenwidth(), self.base.winfo_screenheight()