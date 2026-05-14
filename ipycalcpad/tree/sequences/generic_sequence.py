import ast
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Mapping, Any, ClassVar

from ...protocols import NodeType
from ..node import Node

_SEQ_FORMAT = "\\left[ {data} \\right]"


@dataclass
class GenericSequence(Node):
    elements: tuple[NodeType, ...] = None
    child_fields: ClassVar[tuple[str, ...]] = ('elements',)

    @classmethod
    def from_ast(
            cls,
            node: ast.Tuple|ast.List,
            namespace: Mapping[str,Any],
            children: Sequence[NodeType] = None
    ) -> 'GenericSequence':
        if children:
            return cls(namespace, elements=tuple(children))
        else:
            return cls(namespace, elements=tuple())

    def get_tex(
            self,
            subs: bool = False,
            format_spec: str = None,
            preferred_units: Sequence[str] = None
    ) -> str:
        return _SEQ_FORMAT.format(
            data=' ,\\; '.join(e.get_tex(subs, format_spec, preferred_units) for e in self.elements),
        )

    def get_tex_result(
            self,
            format_spec: str = None,
            preferred_units: Sequence[str] = None
    ) -> str:
        return _SEQ_FORMAT.format(
            data=' ,\\; '.join(e.get_tex_result(format_spec, preferred_units) for e in self.elements),
        )

    def get_result(
            self,
            preferred_units: Sequence[str] = None
    ) -> tuple[Any,...]:
        return tuple(n.get_result(preferred_units) for n in self.elements)

    @property
    def value(self) -> Any:
        return tuple(n.value for n in self.elements)


