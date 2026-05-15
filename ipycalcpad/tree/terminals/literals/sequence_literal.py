from collections.abc import Sequence
from dataclasses import dataclass

from ..literal import Literal
from ....config import Configuration
_C = Configuration()
from ....config.formats import SequenceFormat


@dataclass(kw_only=True)
class SequenceLiteral(Literal):
    obj: Sequence = None

    def get_tex(
            self,
            subs: bool = False,
            format_spec: str = None,
            preferred_units: Sequence[str] = None
    ) -> str:
        return SequenceFormat.format(self.obj, format_spec=format_spec)

    def get_tex_result(
            self,
            format_spec: str = None,
            preferred_units: Sequence[str] = None
    ) -> str:
        return SequenceFormat.format(self.obj, format_spec=format_spec)

