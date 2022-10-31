import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Literal, Tuple, Type, Union

try:
    from PIL.Image import Image
    from PIL.ImageTk import PhotoImage
    HAS_PIL = True
except ImportError:
    Image = tk.Image
    PhotoImage = tk.PhotoImage
    HAS_PIL = False

WidgetType = Union[tk.Widget, ttk.Widget]


class Widget:
    def __init__(self, widget: WidgetType) -> None:
        self.widget = widget

        # To keep the content image alive, here gives a slot to add a
        # reference to the image so that the image wouldn't be recycled by GC
        # at the moment the image adder finishes its work.
        self._image_slot = None

    def grid(self, *args, **kwargs):
        self.widget.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.widget.pack(*args, **kwargs)

    def callback(self, func: Callable[[], Any]):
        self.widget["command"] = func
        return func

    def on(self, seq: str, append: bool = False):
        def __wrapper(func: Callable[[tk.Event], Any]):
            self.widget.bind(seq, func, append)
        return __wrapper

    def destroy(self):
        self.widget.destroy()

    def add_widget(self, sw: Type[WidgetType], *args, **kwargs):
        w = sw(self.widget, *args, **kwargs)
        return Widget(w)

    @property
    def text(self) -> str:
        return self.widget["text"]

    @text.setter
    def text(self, txt: str):
        self.widget["text"] = txt

    @property
    def image(self) -> PhotoImage:  # type: ignore
        return self.widget["image"]

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
        self.widget["image"] = _img

    @property
    def width(self) -> int:
        return self.widget["width"]

    @width.setter
    def width(self, w: int):
        self.widget["width"] = w

    @property
    def height(self) -> int:
        return self.widget["height"]

    @height.setter
    def height(self, h: int):
        self.widget["height"] = h

    @property
    def font(self) -> str:
        return self.widget["font"]

    @font.setter
    def font(self, fon: Union[str, Tuple[str, int], Tuple[str, int, str]]):
        self.widget["font"] = fon


class Window:
    """
    Reformed Window type based on `tkinter`.
    """
    def __init__(self, base: Union[tk.Tk, tk.Toplevel]) -> None:
        """
        Initialize a new window.  
        
        Args:
        - base: `tk.Tk | tk.Toplevel` - base window type
        """
        self.base = base

    def loop(self):
        """
        Run window mainloop.
        """
        self.base.mainloop()

    def destroy(self):
        self.base.destroy()

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

    def on(self, seq: str, append: bool = False):
        def __wrapper(func: Callable[[tk.Event], Any]):
            self.base.bind(seq, func, append)
        return __wrapper

    def on_protocol(self, protocol: str):
        def __wrapper(func: Callable[[], Any]):
            self.base.protocol(protocol, func)
            return func
        return __wrapper

    def add_widget(self, widget: Type[WidgetType], *args, **kwargs):
        w = widget(self.base, *args, **kwargs)
        return Widget(w)