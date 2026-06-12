import ast

from typing import Callable, ClassVar

from .compare import Compare
from ...config import Configuration
_C = Configuration()


class Lt(Compare):
    op_template = _C['comparisons.lt']
    def op_func(self, x, y): return x < y


class Gt(Compare):
    op_template = _C['comparisons.gt']
    def op_func(self, x, y): return x > y


class LtE(Compare):
    op_template = _C['comparisons.lte']

    def op_func(self, x, y): return x <= y


class GtE(Compare):
    op_template = _C['comparisons.gte']

    def op_func(self, x, y): return x >= y


class Eq(Compare):
    op_template = _C['comparisons.eq']
    def op_func(self, x, y): return x == y


COMPARE_OPS: dict[type, Callable] = {
    ast.Lt:  Lt,
    ast.Gt:  Gt,
    ast.LtE: LtE,
    ast.GtE: GtE,
    ast.Eq:  Eq,
}

__all__ = ['Lt', 'Gt', 'LtE', 'GtE', 'Eq', 'COMPARE_OPS']
