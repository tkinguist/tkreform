import tkinter as tk
from tkreform import Window
from tkreform.declarative import W, Gridder, Packer

win = Window(tk.Tk())

win.title = "Window Title"
win.size = 600, 400
win.resizable = False
win.top = True

win /= (
    W(tk.Label, bg="gray", width=25, height=40) * Gridder(),
    W(tk.Frame, width=350, height=400) * Gridder(column=1, row=0, sticky="nw") / (
        W(tk.Frame, width=350, height=350) * Gridder() / (
            W(tk.Label, text="Title", font=("Segoe UI", 20)) * Gridder(padx=5, pady=5, sticky="nw"),
            W(tk.Message, text="abcd\nefgh", font=("Segoe UI", 12), width=380) * Gridder(row=1, padx=5, pady=5, sticky="nw")
        ),
        W(tk.Frame, width=350, height=50) * Gridder(row=1, sticky="se", padx=5, pady=5) / (
            W(tk.Button, text="Exit") * Packer(side="right"),
            W(tk.Button, text="Continue") * Packer(side="right")
        )
    )
)

win[1][1][0].callback(win.destroy)

win.loop()