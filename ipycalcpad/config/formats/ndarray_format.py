from numpy import ndarray

from ..format import Format
from ..config import Configuration
_C = Configuration()

_MATRIX_TEMPLATE = "\\begin{{bmatrix}} {data} \\end{{bmatrix}}"
_MAT_ITEM_SEP = r" & "
_MAT_ROW_SEP = r" \\ "
_VEC_ITEM_SEP = r" \\ "


class NDArrayFormat(Format):
    types_to_format = (ndarray,)

    @classmethod
    def format(cls, value: ndarray, format_spec:str=None) -> str:
        match value.ndim:
            case 1:
                tex_out = cls._format_1D(value, format_spec)
            case 2:
                tex_out = cls._format_2D(value, format_spec)
            case _:
                tex_out = cls._format_ND(value, format_spec)

        return _MATRIX_TEMPLATE.format(data=tex_out)

    @classmethod
    def _format_1D(
            cls,
            array: ndarray,
            format_spec: str = None
    ) -> str:
        return (
            _VEC_ITEM_SEP.join(
                _C.format_object(colj, format_spec=format_spec)
                for colj in array
            )
        )

    @classmethod
    def _format_2D(
            cls,
            array: ndarray,
            format_spec: str = None
    ) -> str:
        return (
            _MAT_ROW_SEP.join(
                _MAT_ITEM_SEP.join(
                    _C.format_object(colj, format_spec=format_spec)
                    for colj in rowi)
                for rowi in array
            )
        )

    @classmethod
    def _format_ND(
            cls,
            array: ndarray,
            format_spec: str = None
    ) -> str:
        raise NotImplementedError("N-Dimensional arrays are not supported yet.")

