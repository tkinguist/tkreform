import tkinter
from typing import Any, Callable, Dict, List, Tuple, Union

from tkreform.base import Widget, Window
from tkreform.declarative import Gridder


class Group:
    def __init__(self, *content: Union["Group", Widget, Window]) -> None:
        self._contents = content

    def __getitem__(self, it: Union[int, slice]):
        return self._contents[it]


class ActionGroup(Group):
    _contents: Tuple[Union["ActionGroup", Widget, Window]]

    def __init__(self, *ct: Union["ActionGroup", Widget, Window]) -> None:
        self._calls: Dict[str, List[Callable[[tkinter.Event], Any]]] = {}
        super().__init__(*ct)

    def _setup_dict(self, seq: str):
        if seq not in self._calls:
            for co in self._contents:
                def call(event: tkinter.Event):
                    for ca in self._calls[seq]:
                        ca(event)

                co.on(seq, append=True)(call)
            self._calls[seq] = []

    def on(self, seq: str, append: bool = False):
        self._setup_dict(seq)

        def __wrapper(func: Callable[[tkinter.Event], Any]):
            if append:
                self._calls[seq].append(func)
            else:
                self._calls[seq] = [func]
            return func
        return __wrapper


class GriddingGroup(Group):
    _contents: Tuple[Widget]

    def grid(self, columnspan: int, **kwargs):
        for idx, wi in enumerate(self._contents):
            wi.grid(
                column=idx // columnspan, columnspan=columnspan,
                row=idx % columnspan, **kwargs
            )

    def __mul__(self, other: Gridder):
        if other.columnspan is None:
            raise ValueError(
                "'GriddingGroup' requires 'Gridder' to have columnspan."
            )
        self.grid(
            columnspan=other.columnspan, rowspan=other.rowspan,
            ipadx=other.ipadx, ipady=other.ipady, padx=other.padx,
            pady=other.pady, sticky=other.sticky
        )
        return self
