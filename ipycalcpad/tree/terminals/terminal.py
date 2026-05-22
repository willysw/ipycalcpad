import math

from collections.abc import Sequence
from dataclasses import dataclass, KW_ONLY
from typing import Any, ClassVar, Type

from ..node import Node

from ...config import Configuration
_C = Configuration()

_DEFAULT_TEMPLATE:str = '{{{object}}}'


@dataclass
class Terminal(Node):
    _:KW_ONLY
    obj: Any = None
    template_key: ClassVar[str] = ''

    def get_tex(
            self,
            subs: bool = False,
            format_spec: str|None = None,
            preferred_units: Sequence[str]|None = None
    ) -> str:
        reduced_obj = _C.reduce_units(self.obj, preferred_units=preferred_units)
        return self.template.format(
            object=_C.format_object(reduced_obj, format_spec=format_spec)
        )

    @property
    def value(self) -> Any:
        if self.obj is not None:
            return self.obj
        else:
            return math.nan

    @property
    def type(self) -> Type:
        return type(self.obj)

    @property
    def template(self) -> str:
        if self.__class__.template_key:
            return _C[self.__class__.template_key]
        else:
            return _DEFAULT_TEMPLATE


__all__ = ['Terminal']
