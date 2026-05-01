import ast
import math

from collections.abc import Sequence, Mapping
from dataclasses import dataclass, field
from typing import Any, ClassVar

from ..protocols import NodeType

from ..config import Configuration
_C = Configuration()


@dataclass
class Node(NodeType):
    ast_node: ast.AST = field(repr=False)
    namespace: Mapping[str,Any] = field(repr=False)
    node_precedence: ClassVar[int] = 100000
    child_fields: ClassVar[tuple[str, ...]] = tuple()

    @classmethod
    def from_ast(
            cls,
            node: ast.expr,
            namespace: Mapping[str,Any],
            children: Sequence[NodeType]
    ) -> 'Node':
        return cls(node, namespace)

    def get_tex(self, subs: bool = False) -> str:
        return f'\\texttt{{{self.__class__.__name__}}}'

    def get_tex_result(self) -> str:
        return _C.format_object(self.value)

    def get_result(self):
        return _C.reduce_units(self.value)

    @property
    def value(self) -> Any:
        return math.nan

    @property
    def text(self) -> str:
        if self.ast_node:
            return ast.unparse(self.ast_node)
        else:
            return ''

    @property
    def has_substituted_fields(self) -> bool:
        for field_name in self.child_fields:
            if hasattr(self, field_name):
                field_node = getattr(self, field_name)
                if (isinstance(field_node, NodeType) and
                    field_node.has_substituted_fields):
                    return True
                if isinstance(field_node, Sequence):
                    for node in field_node:
                        if (isinstance(node, NodeType) and
                            node.has_substituted_fields):
                            return True
                if isinstance(field_node, Mapping):
                    for node in field_node.values():
                        if (isinstance(node, NodeType) and
                            node.has_substituted_fields):
                            return True
        # default to False
        return False


    @staticmethod
    def parens_by_precedence(precedence: int, other: NodeType, subs: bool = False) -> str:
        if precedence > other.node_precedence:
            return f'\\left({other.get_tex(subs)}\\right)'
        else:
            return other.get_tex(subs)


__all__ = ['Node']