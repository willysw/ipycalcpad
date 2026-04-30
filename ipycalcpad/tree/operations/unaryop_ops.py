import ast

from typing import Callable

from .unaryop import UnaryOp

from ...config import Configuration
_C = Configuration()


class Neg(UnaryOp):
    node_precedence = 20
    operand_precedence = 15
    op_template = _C['unary_ops.neg']
    def op_func(self, x): return -x


class Pos(UnaryOp):
    node_precedence = 20
    operand_precedence = 15
    op_template = _C['unary_ops.pos']
    def op_func(self, x): return x


class Not(UnaryOp):
    node_precedence = 10
    operand_precedence = 15
    op_template = _C['unary_ops.not']
    def op_func(self, x): return not x


class Invert(UnaryOp):
    node_precedence = 10
    operand_precedence = 15
    op_template = _C['unary_ops.not']
    def op_func(self, x): return ~x


UNARY_OPS: dict[type, Callable] = {
    ast.USub:   Neg,
    ast.UAdd:   Pos,
    ast.Not:    Not,
    ast.Invert: Invert,
}


__all__ = ['Neg', 'Pos', 'Not', 'Invert', 'UNARY_OPS']
