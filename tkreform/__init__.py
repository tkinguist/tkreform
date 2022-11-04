"""
Reformed tkinter coding tool.

TkReform provides a wrapping on standard Tkinter. Window wraps Toplevel
widgets, and Widget wraps other widgets.

Properties of the widgets can be specified with keyword arguments or
attributes.

Example (Hello, World):
>>> import tkinter as tk
>>> import tkreform
>>> window = tkreform.Window(tk.Tk())
>>> frame = window.add_widget(tk.Frame, relief="ridge", borderwidth=2)
>>> frame.pack(fill="both", expand=True)
>>> label = frame.add_widget(tk.Label)
>>> label.text = "Hello, World"
>>> label.pack(fill="x", expand=True)
>>> button = frame.add_widget(tk.Button, text="Exit")
>>> button.callback(window.destroy)
>>> button.pack(side="bottom")
>>> window.loop()
"""

from tkreform import base, declarative, groups
from tkreform.base import dec, Widget, Window
from tkreform.declarative import Gridder, Packer, Placer

__all__ = [
    "base", "dec", "declarative", "groups", "Widget", "Window", "Gridder",
    "Packer", "Placer"
]
