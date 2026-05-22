from collections.abc import Sequence
from dataclasses import dataclass

from numpy import ndarray

from ..literal import Literal
from ....config import Configuration
_C = Configuration()
from ....config.formats import NDArrayFormat


@dataclass(kw_only=True)
class ArrayLiteral(Literal):
    obj: ndarray = None

    def get_tex(
            self,
            subs: bool = False,
            format_spec: str|None = None,
            preferred_units: Sequence[str]|None = None
    ) -> str:
        return NDArrayFormat.format(self.obj, format_spec)

    def get_tex_result(
            self,
            format_spec: str|None = None,
            preferred_units: Sequence[str]|None = None
    ) -> str:
        return NDArrayFormat.format(self.obj, format_spec)
