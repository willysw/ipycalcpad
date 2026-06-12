__all__ = ['COMPARE_OPS', 'Lt', 'Gt', 'LtE', 'GtE', 'Eq', 'CompareOp']

import ast

from typing import Callable, ClassVar

from ipycalcpad.protocols import NodeType
from ipycalcpad.config import Configuration
_C = Configuration()


class CompareOp:
    op_template: ClassVar[str] = _C['comparisons.unknown_op']
    op_func: ClassVar[Callable[[NodeType,NodeType],bool]] = lambda x, y: False


class Lt(CompareOp):
    op_template = _C['comparisons.lt']
    op_func = lambda x, y: x < y


class Gt(CompareOp):
    op_template = _C['comparisons.gt']
    op_func = lambda x, y: x > y


class LtE(CompareOp):
    op_template = _C['comparisons.lte']
    op_func = lambda x, y: x <= y


class GtE(CompareOp):
    op_template = _C['comparisons.gte']
    op_func = lambda x, y: x >= y


class Eq(CompareOp):
    op_template = _C['comparisons.eq']
    op_func = lambda x, y: x == y


# noinspection PyTypeChecker
COMPARE_OPS: dict[type, CompareOp] = {
    ast.Lt:  Lt,
    ast.Gt:  Gt,
    ast.LtE: LtE,
    ast.GtE: GtE,
    ast.Eq:  Eq,
}
