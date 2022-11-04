from abc import ABCMeta, abstractmethod, abstractproperty
import gettext
import locale
from typing import Iterable, Optional

from tkreform.exceptions import MessageNotFound


class Messages(dict[str, str]):
    def __matmul__(self, __o: str) -> str:
        for k in self:
            if self[k] == __o:
                return k
        raise MessageNotFound(f"Cannot find any key by value '{__o}'.")


class Linguist(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, text: str):
        raise NotImplementedError

    @abstractproperty
    def dest(self) -> str:
        raise NotImplementedError

    @dest.setter
    def dest(self, _new: str):
        raise NotImplementedError


class KVPairLinguist(Linguist):
    def __init__(
        self, lc_base: str, lc_fallback: Iterable[str], **kwargs: Messages
    ) -> None:
        self._base = lc_base
        self._messages = kwargs
        self._fallback = lc_fallback
        self.default_locale, _ = locale.getdefaultlocale()  # type: ignore
        self._dest: str = self.default_locale

    def __getitem__(self, text: str):
        key = self._messages[self._base] @ text
        return self._messages[self._dest][key]

    @property
    def dest(self) -> str:
        return self._dest

    @dest.setter
    def dest(self, _new: str):
        self._dest = _new

    @property
    def current_messages(self):
        return self._messages[self.dest]


class GettextLinguist(Linguist):
    def __init__(
        self, domain: str, dest: str, lc_fallback: Iterable[str],
        lc_path: Optional[str] = None
    ) -> None:
        self.domain = domain
        self._fallback = lc_fallback
        self._lcpath = lc_path
        self.tr = gettext.translation(
            domain, lc_path, (dest, *lc_fallback), fallback=True
        )
        self._dest = dest

    def __getitem__(self, text: str):
        return self.tr.gettext(text)

    @property
    def dest(self) -> str:
        return self._dest

    @dest.setter
    def dest(self, _new: str):
        self._dest = _new
        self.tr = gettext.translation(
            self.domain, self._lcpath, (_new, *self._fallback), fallback=True
        )
