import ast
import math
import pint

from collections.abc import Sequence, Mapping
from dataclasses import dataclass, KW_ONLY
from typing import Any, ClassVar

from ...protocols import NodeType
from ..node import Node
from ..terminals import Literal

from ...config import Configuration
_C = Configuration()

_DEFAULT_TEMPLATE = _C['unary_ops.unknown_op']


@dataclass
class UnaryOp(Node):
    _:KW_ONLY
    operand: NodeType = None
    child_fields: ClassVar[tuple[str, ...]] = ('operand',)
    node_precedence: ClassVar[int] = 0
    operand_precedence: ClassVar[int] = 0
    op_template: ClassVar[str] = _DEFAULT_TEMPLATE

    @classmethod
    def from_ast(
            cls,
            node: ast.UnaryOp,
            namespace: Mapping[str,Any],
            children: Sequence[NodeType]
    ) -> NodeType:
        from .unaryop_ops import UNARY_OPS
        if type(node.op) in UNARY_OPS:
            if isinstance(node.op, ast.UAdd):
                return children[0]

            if (isinstance(node.op, ast.USub)
                and isinstance(children[0], Literal)
                and isinstance(children[0].obj, (int, float, pint.Quantity))):
                return Literal(node, namespace, obj=-children[0].obj)

            return UNARY_OPS[type(node.op)](node, namespace, operand=children[0])

        else:
            return cls(node, namespace, operand=children[0])

    def op_func(self, x): return math.nan

    def get_tex(self, subs: bool = False) -> str:
        return self.op_template.format(operand=self.operand_tex(subs))

    @property
    def value(self) -> Any:
        if self.op_func:
            return getattr(self,'op_func')(self.operand.value)
        else:
            return math.nan

    def operand_tex(self, subs: bool = False) -> str:
        return self.parens_by_precedence(self.operand_precedence, self.operand, subs)


__all__ = ['UnaryOp']

