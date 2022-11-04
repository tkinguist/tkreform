import tkinter as tk
from tkreform import Window
from tkreform.declarative import W, Gridder, Packer
from tkreform import linguist

win = Window(tk.Tk())

en_US = linguist.Messages(
    {
        "win.title": "Window Title",
        "text.title": "Title",
        "text.msgx": "abcd\nefgh",
        "button.exit": "Exit",
        "button.continue": "Continue"
    }
)

zh_CN = linguist.Messages(
    {
        "win.title": "窗口标题",
        "text.title": "标题",
        "text.msgx": "锟斤拷锟斤拷\n烫烫烫烫烫烫",
        "button.exit": "退出",
        "button.continue": "继续"
    }
)

lin = linguist.KVPairLinguist("en_US", ("en_US", ), en_US=en_US, zh_CN=zh_CN)
win.linguist = lin

win.title = "Window Title"
win.size = 600, 400
win.resizable = False
win.top = True

win /= (
    W(tk.Label, bg="gray", width=25, height=40) * Gridder(),
    W(tk.Frame, width=350, height=400) * Gridder(column=1, row=0, sticky="nw") / (
        W(tk.Frame, width=350, height=350) * Gridder() / (
            W(tk.Label, text="Title", font=("Microsoft Yahei UI", 20)) * Gridder(padx=5, pady=5, sticky="nw"),
            W(tk.Message, text="abcd\nefgh", font=("Microsoft Yahei UI", 12), width=380) * Gridder(row=1, padx=5, pady=5, sticky="nw")
        ),
        W(tk.Frame, width=350, height=50) * Gridder(row=1, sticky="se", padx=5, pady=5) / (
            W(tk.Button, text="Exit", font=("Microsoft Yahei UI", )) * Packer(side="right"),
            W(tk.Button, text="Continue", font=("Microsoft Yahei UI", )) * Packer(side="right")
        )
    )
)

win[1][1][0].callback(win.destroy)  # type: ignore

win.loop()