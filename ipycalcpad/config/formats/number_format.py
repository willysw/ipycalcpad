from typing import cast

from ..format import Format

from ..config import Configuration
_C = Configuration()

_INT_FMT = cast(str, _C['objects.integer'])
_REAL_FMT = cast(str, _C['objects.decimal'])


class NumberFormat(Format):
    types_to_format = (int, float)

    @classmethod
    def format(cls, value: str, format_spec:str='') -> str:
        if format_spec:
            fmt_spec = format_spec
        elif isinstance(value, int) and _INT_FMT:
            fmt_spec = _INT_FMT
        elif isinstance(value, float) and _REAL_FMT:
            fmt_spec = _REAL_FMT
        else:
            return str(value)

        return f'{value:{fmt_spec}}'


__all__ = ['NumberFormat']
