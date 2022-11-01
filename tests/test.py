import tkreform, tkinter as tk, tkinter.ttk as ttk

win = tkreform.Window(tk.Tk())

win.title = "Window Title"
win.size = 600, 400
win.resizable = False
win.top = True

w1 = win.add_widget(tk.Label, bg="gray")
w1.size = 25, 400
w1.grid(column=0, row=0)

tf = win.add_widget(tk.Frame)
tf.grid(column=1, row=0, sticky="NW")

f1 = tf.add_widget(tk.Frame)
f1.grid()

f2 = tf.add_widget(tk.Frame)
f2.grid(row=1, sticky="SE", padx=5, pady=5)
f2.width = 350
f2.height = 50

w2 = f1.add_widget(ttk.Label)
w2.text = "Title"
w2.font = "Segoe UI", 20
w2.grid(padx=5, pady=5, sticky="NW")

w3 = f1.add_widget(tk.Message)
w3.text = "A quick brown fox jumps over the lazy dog.\n"\
    "texttexttexttexttexttexttexttexttexttexttexttexttexttexttexttexttexttexttexttexttexttext"
w3.font = "Segoe UI", 12
w3.grid(row=1, padx=5, pady=5, sticky="NW")
w3.width = 380

b1 = f2.add_widget(ttk.Button)
b1.text = "Exit"
b1.pack(side="right")
b1.callback(win.destroy)

b2 = f2.add_widget(ttk.Button)
b2.text = "Continue"
b2.pack(side="right")

win.loop()