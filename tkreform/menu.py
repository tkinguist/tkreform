from tkinter import Menu
from tkreform.exceptions import MenuNotBinded


class MenuItem:
    def __init__(self, type: str, **kwargs):
        self.type = type
        self.data = kwargs
        self.base = None

    def bind_menu(self, m: Menu, **kwargs):
        # self.base = Menu(m, **kwargs)
        self.base = m

    def _add_item(self, type: str, **kwargs):
        if self.base is None:
            raise MenuNotBinded
        self.base.add(type, **kwargs)

    def add_item(self, it: "MenuItem"):
        if self.base is None:
            raise MenuNotBinded
        it.bind_menu(self.base)
        self._add_item(it.type, **it.data)


class MenuCascade(MenuItem):
    def __init__(self, **kwargs):
        super().__init__("cascade", **kwargs)


class MenuCheckbutton(MenuItem):
    def __init__(self, **kwargs):
        super().__init__("checkbutton", **kwargs)


class MenuCommand(MenuItem):
    def __init__(self, **kwargs):
        super().__init__("command", **kwargs)


class MenuRadioButton(MenuItem):
    def __init__(self, **kwargs):
        super().__init__("radiobutton", **kwargs)


class MenuSeparator(MenuItem):
    def __init__(self, **kwargs):
        super().__init__("separator", **kwargs)
