from collections.abc import Sequence
from typing import Any

from ..format import Format
from ..config import Configuration
_C = Configuration()

_SEQ_FORMAT = "\\left( {data} \\right)"
_SEQ_ITEM_SEP = r" ,\; "


class SequenceFormat(Format):
    types_to_format = (Sequence,)

    @classmethod
    def format(cls, value: Any, format_spec:str=None) -> str:
        return cls._row_tex(value, format_spec)

    @classmethod
    def _row_tex(
            cls,
            elements: Sequence,
            format_spec: str = None
    ) -> str:
        element_tex = []
        for el in elements:
            if isinstance(el, Sequence):
                element_tex.append(cls._row_tex(el, format_spec))
            else:
                element_tex.append(_C.format_object(el, format_spec))
        return _SEQ_FORMAT.format(data=_SEQ_ITEM_SEP.join(element_tex))


__all__ = ['SequenceFormat']