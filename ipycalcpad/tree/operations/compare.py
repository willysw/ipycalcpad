import ast

from collections.abc import Sequence, Mapping
from dataclasses import dataclass, KW_ONLY, field
from typing import Any, ClassVar

from .compare_ops import CompareOp, COMPARE_OPS
from ipycalcpad.protocols import NodeType
from ipycalcpad.tree.node import Node
from ipycalcpad.config import Configuration
_C = Configuration()

_DEFAULT_TEMPLATE = _C['comparisons.unknown_op']


@dataclass
class Compare(Node):
    _:KW_ONLY
    operands: list[NodeType] = field(default_factory=list)
    operators: list[CompareOp] = field(default_factory=list)
    child_fields: ClassVar[tuple[str, ...]] = ('left', 'comparitors')
    op_template: ClassVar[str] = _DEFAULT_TEMPLATE

    @classmethod
    def from_ast(
            cls,
            node: ast.Compare,
            namespace: Mapping[str,Any],
            children: Sequence[NodeType]
    ) -> 'Compare':
        operands = children
        operators = [COMPARE_OPS[type(op_i)] for op_i in node.ops]
        return cls(namespace,
                   operators=operators, # type: ignore
                   operands=operands) # type: ignore

    def get_tex(
            self,
            subs: bool = False,
            format_spec: str|None = None,
            preferred_units: Sequence[str]|None = None
    ) -> str:
        operand_tex = [opnd.get_tex(subs, format_spec, preferred_units)
                       for opnd in self.operands]
        out = operand_tex[0]
        for op_i, opnd_i in zip(self.operators, operand_tex[1:]):
            out = op_i.op_template.format(left=out, right=opnd_i)
        return out


    @property
    def value(self) -> bool:
        opnd_vals = (opnd.value for opnd in self.operands)
        val_i_1 = next(opnd_vals)
        for op_i, val_i in zip(self.operators, opnd_vals):
            check = op_i.op_func(val_i_1, val_i)
            if not check:
                return False
            val_i_1 = val_i
        return True


__all__ = ['Compare']
