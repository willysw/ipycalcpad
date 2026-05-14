
from collections.abc import Sequence
from numpy import asarray
from typing import Any

from ..format import Format
from ..config import Configuration
_C = Configuration()

_VECTOR_TEMPLATE = "\\begin{{bmatrix}} {data} \\end{{bmatrix}}"
_MATRIX_TEMPLATE = "\\begin{{bmatrix}} {data} \\end{{bmatrix}}"
_HETERO_FORMAT = "\\left[ {data} \\right]"


class SequenceFormat(Format):
    types_to_format = (Sequence,)

    @classmethod
    def format(cls, value: Any, format_spec:str=None) -> str:

        shape = cls.get_shape(value)
        if shape and len(shape) == 1:
            return cls.format_1D(value, format_spec)
        elif shape and len(shape) == 2:
            return cls.format_2D(value, format_spec)
        else:
            return cls.format_generic(value, format_spec)

    @classmethod
    def format_1D(cls, value: Any, format_spec:str=None) -> str:
        return _VECTOR_TEMPLATE.format(
            data=r' \\ '.join(
                _C.format_object(i, format_spec=format_spec) for i in value
            )
        )

    @classmethod
    def format_2D(cls, value: Any, format_spec:str=None) -> str:
        return _MATRIX_TEMPLATE.format(
            data=r' \\ '.join(
                r' & '.join(
                    _C.format_object(i, format_spec=format_spec) for i in row
                ) for row in value
            )
        )

    @classmethod
    def format_generic(cls, value: Any, format_spec:str=None) -> str:
        return _HETERO_FORMAT.format(
            data=' ,\\; '.join(_C.format_object(i, format_spec=format_spec) for i in value)
        )

    @staticmethod
    def get_shape(value: Any) -> tuple[int,...]|None:
        try:
            # This only works if the sequence has homgeneous elements.
            return asarray(value).shape
        except ValueError:
            # The sequence is heterogeneous.
            return None

__all__ = ['SequenceFormat']