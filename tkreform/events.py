from typing import Tuple, Union

DETAIL = 1
TYPE = 2
MODIFIER = 3
NMODIFIER = 4

KEY_LITERAL_SEP = "+"


_negative_event = {
    "Key": "KeyRelease",
    "KeyRelease": "Key",
    "KeyPress": "KeyRelease",
    "Button": "ButtonRelease",
    "ButtonRelease": "Button",
    "ButtonPress": "ButtonRelease",
    "Enter": "Leave",
    "Leave": "Enter",
    "FocusIn": "FocusOut",
    "FocusOut": "FocusIn"
}


class Event:
    def __init__(self, *eventdata: Tuple[str, str, int]) -> None:
        _eventdata = set(eventdata)
        self._ed = sorted(_eventdata, key=lambda x: (-x[2], x[1]))

    @property
    def literal(self):
        return KEY_LITERAL_SEP.join(x[0] for x in self._ed if x[0])

    @property
    def event(self):
        return f"<{'-'.join(x[1] for x in self._ed if x[1])}>"

    def __str__(self) -> str:
        return self.event

    def __repr__(self) -> str:
        return f"Event({self.event})"

    def __hash__(self):
        return hash(self.event)

    def __add__(self, other: Union["Event", int, str]):
        if not isinstance(other, Event):
            _other = str(other)
            o = type(self)((_other, _other, DETAIL))
        else:
            o = other
        return type(self)(*self._ed, *o._ed)

    def __sub__(self, other: Union["Event", int, str]):
        return self + other

    def __and__(self, other: Union["Event", int, str]):
        return self + other

    def __or__(self, other: Union["Event", int, str]):
        return self + other

    def __neg__(self):
        return type(self)(
            *tuple(
                (name, _negative_event[event], ord)
                if event in _negative_event else
                (name, event, ord) for name, event, ord in self._ed
            )
        )


KEY = Event(("", "Key", TYPE))
CTRL = Event(("Ctrl", "Control", MODIFIER))
ALT = Event(("Alt", "Alt", MODIFIER))
SHIFT = Event(("Shift", "Shift", MODIFIER))
CAPS = Event(("CapsLock", "Lock", MODIFIER))


def FN(n: int):
    return Event((f"F{n}", f"F{n}", TYPE))


X2 = Event(("", "Double", NMODIFIER))
X3 = Event(("", "Triple", NMODIFIER))
X4 = Event(("", "Quadruple", NMODIFIER))

LMB = Event(("Left Mouse Button", "Button", TYPE), ("", "1", DETAIL))
RMB = Event(("Right Mouse Button", "Button", TYPE), ("", "3", DETAIL))
CMB = Event(("Middle Mouse Button", "Button", TYPE), ("", "2", DETAIL))
