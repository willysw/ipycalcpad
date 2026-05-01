import math

from dataclasses import dataclass, KW_ONLY
from typing import Any, ClassVar, Type

from ..node import Node

from ...config import Configuration
_C = Configuration()

_TEMPLATE:str = '{{{object}}}'


@dataclass
class Terminal(Node):
    _:KW_ONLY
    obj: Any = None
    template: ClassVar[str] = _TEMPLATE

    def get_tex(self, subs: bool = False) -> str:
        return self.template.format(object=_C.format_object(self.obj))

    @property
    def value(self) -> Any:
        if self.obj is not None:
            return self.obj
        else:
            return math.nan

    @property
    def type(self) -> Type:
        return type(self.obj)


__all__ = ['Terminal']
