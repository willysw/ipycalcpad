import pint
import re

from typing import cast, Any

from ..format import Format

from ..config import Configuration
_C = Configuration()

_DEC_SPEC = cast(str, _C['objects.decimal'])
_PINT_SPEC = cast(str, _C['objects.pint_quantity'])
_PINT_SPEC_RE = re.compile(r"(D|P|H|L|Lx|C|#|~|\^)")


class PintFormat(Format):
    types_to_format = (pint.Quantity,)

    @classmethod
    def format(cls, value: Any, format_spec:str=None) -> str:
        if format_spec:
            # check if format spec contains pint specifiers. If so, assume
            # the spec is a complete pint specifier.
            if _PINT_SPEC_RE.search(format_spec):
                fmt_spec = format_spec
            else:
                fmt_spec = _PINT_SPEC.format(number_spec=format_spec)
        else:
            fmt_spec = _PINT_SPEC.format(number_spec=_DEC_SPEC)

        return f'{value:{fmt_spec}}'


__all__ = ['PintFormat']
