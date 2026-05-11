import re

from typing import cast

from ..format import Format

from ..config import Configuration
_C = Configuration()

_INT_FMT = cast(str, _C['objects.integer'])
_REAL_FMT = cast(str, _C['objects.decimal'])
_PINT_SPEC_RE = re.compile(r"(D|P|H|L|Lx|C|#|~|\^)")


class NumberFormat(Format):
    types_to_format = (int, float)

    @classmethod
    def format(cls, value: str, format_spec:str='') -> str:
        if isinstance(value, int) and _INT_FMT:
            fmt_spec = _INT_FMT
        elif format_spec:
            fmt_spec = _PINT_SPEC_RE.sub(repl="", string=format_spec)
        elif isinstance(value, float) and _REAL_FMT:
            fmt_spec = _REAL_FMT
        else:
            return str(value)

        return f'{value:{fmt_spec}}'


__all__ = ['NumberFormat']
