import ast

from collections.abc import Sequence, Mapping
from dataclasses import dataclass, KW_ONLY
from math import nan
from typing import Any, ClassVar

from ...protocols import NodeType
from ..node import Node

from ...config import Configuration
_C = Configuration()

_DEFAULT_TEMPLATE = _C['binary_ops.unknown_op']


@dataclass
class BinOp(Node):
    _:KW_ONLY
    left: NodeType = None
    right: NodeType = None
    child_fields: ClassVar[tuple[str, ...]] = ('left', 'right')
    node_precedence: ClassVar[int] = 0
    left_precedence: ClassVar[int] = 0
    right_precedence: ClassVar[int] = 0
    op_template: ClassVar[str] = _DEFAULT_TEMPLATE

    @classmethod
    def from_ast(
            cls,
            node: ast.BinOp,
            namespace: Mapping[str,Any],
            children: Sequence[NodeType]
    ) -> 'BinOp':
        from .binop_ops import BINARY_OPS
        if type(node.op) in BINARY_OPS:
            return BINARY_OPS[type(node.op)](node, namespace, left=children[0], right=children[1])
        else:
            return cls(node, namespace, left=children[0], right=children[1])

    def op_func(self, x, y): return nan

    def get_tex(self, subs: bool = False) -> str:
        return (self.op_template
                .format(left=self.left_tex(subs),
                        right=self.right_tex(subs)))

    @property
    def value(self) -> Any:
        if self.op_func:
            return getattr(self,'op_func')(self.left.value, self.right.value)
        else:
            return nan

    def left_tex(self, subs: bool = False) -> str:
        return self.parens_by_precedence(self.left_precedence, self.left, subs)

    def right_tex(self, subs: bool = False) -> str:
        return self.parens_by_precedence(self.right_precedence, self.right, subs)


__all__ = ['BinOp']

