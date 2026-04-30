import ast

from typing import Callable, ClassVar

from .binop import BinOp
from .. import Literal
from ...protocols import NodeType
from ..terminals import Variable
from ..callable import Func

from ...config import Configuration
_C = Configuration()


class Add(BinOp):
    """
    Represents an addition binary operation.
    """
    node_precedence = 10
    left_precedence = 10
    right_precedence = 10
    op_template = _C['binary_ops.add']
    def op_func(self, x, y): return x + y


class Sub(BinOp):
    """
    Represents a subtraction binary operation.
    """
    node_precedence = 10
    left_precedence = 10
    right_precedence = 15
    op_template = _C['binary_ops.sub']
    def op_func(self, x, y): return x - y


class Mult(BinOp):
    """
    Represents a multiplication binary operation.
    """
    node_precedence = 20
    left_precedence = 20
    right_precedence = 20
    op_template = _C['binary_ops.mult']
    op_template_short = _C['binary_ops.mult_short']
    left_types: ClassVar[tuple[type, ...]] = (Variable,)
    right_types: ClassVar[tuple[type, ...]] = (Variable, Func)
    literal_types: ClassVar[tuple[type, ...]] = (Literal,)
    def op_func(self, x, y): return x * y

    def get_tex(self, subs: bool = False) -> str:
        if subs:
            return self.op_template.format(left=self.left_tex(True),
                                           right=self.right_tex(True))
        else:
            if Mult._is_short(self.left, self.right):
                return self.op_template_short.format(left=self.left_tex(False),
                                                    right=self.right_tex(False))
            else:
                return self.op_template.format(left=self.left_tex(False),
                                               right=self.right_tex(False))
    
    @classmethod
    def _is_short(cls, left:NodeType, right:NodeType) -> bool:

        """
        Check if short multiplication notation can be used.

        Determines whether the multiplication can be rendered without
        an explicit operator symbol (e.g., 'ab' instead of 'a·b').

        Parameters
        ----------
        left : NodeType
            The left operand of the Mult.
        right : NodeType
            The right operand of the Mult.

        Returns
        -------
        bool
            True if short notation can be used, False otherwise.
        """
        return (
                (
                    isinstance(left, cls.left_types) or
                    isinstance(left, cls.literal_types) or
                    (isinstance(left, Mult) and cls._recurse_left_mult(left))
                )
                and
                (
                    isinstance(right, cls.right_types) or
                    (isinstance(right, Mult) and cls._recurse_right_mult(right))
                )
            )
    
    @classmethod
    def _recurse_left_mult(cls, node:Mult) -> bool:
        """
        Recurse the right branch of the left node.
        """
        if (isinstance(node.right, cls.left_types) or
            isinstance(node.right, cls.literal_types)):
            return True
        elif isinstance(node.right, Mult):
            return cls._recurse_left_mult(node.right)
        else:
            return False
        
    @classmethod
    def _recurse_right_mult(cls, node:Mult) -> bool:
        """
        Recurse the left branch of the right node.
        """
        if isinstance(node.left, cls.right_types):
            return True
        elif isinstance(node.left, Mult):
            return cls._recurse_left_mult(node.left)
        else:
            return False


class Div(BinOp):
    """
    Represents a division binary operation.
    """
    node_precedence = 20
    left_precedence = -1
    right_precedence = -1
    op_template = _C['binary_ops.div']
    def op_func(self, x, y): return x / y


class Pow(BinOp):
    """
    Represents a power/exponentiation binary operation.
    """
    node_precedence = 30
    left_precedence = 30
    right_precedence = 20
    op_template = _C['binary_ops.pow']
    def op_func(self, x, y): return x ** y


class Mod(BinOp):
    """
    Represents a modulo binary operation.
    """
    node_precedence = 20
    left_precedence = 20
    right_precedence = 25
    op_template = _C['binary_ops.mod']
    def op_func(self, x, y): return x % y


BINARY_OPS: dict[type, Callable] = {
    ast.Add:  Add,
    ast.Sub:  Sub,
    ast.Mult: Mult,
    ast.Div:  Div,
    ast.Pow:  Pow,
    ast.Mod:  Mod
}


__all__ = ['Add', 'Sub', 'Mult', 'Div', 'Pow', 'Mod', 'BINARY_OPS']