import pint

from typing import cast, Any

from ..format import Format

from ..config import Configuration
_C = Configuration()

_PINT_SPEC = cast(str, _C['objects.pint_quantity'])


class PintFormat(Format):
    types_to_format = (pint.Quantity,)

    @classmethod
    def format(cls, value: Any, format_spec:str='') -> str:
        if format_spec:
            fmt_spec = format_spec
        elif _PINT_SPEC:
            fmt_spec = _PINT_SPEC
        else:
            fmt_spec = '.4g~L'

        return f'{value:{fmt_spec}}'


__all__ = ['PintFormat']
