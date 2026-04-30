import math

from dataclasses import dataclass, KW_ONLY
from typing import Any, ClassVar

from ..node import Node

from ...config import format_object

_TEMPLATE:str = '{{{object}}}'


@dataclass
class Terminal(Node):
    _:KW_ONLY
    obj: Any = None
    template: ClassVar[str] = _TEMPLATE

    def get_tex(self, subs: bool = False) -> str:
        return self.template.format(object=format_object(self.obj))

    @property
    def value(self) -> Any:
        if self.obj:
            return self.obj
        else:
            return math.nan

    @property
    def type(self) -> Any:
        return type(self.obj)


__all__ = ['Terminal']
