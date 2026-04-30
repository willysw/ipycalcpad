import ast
from dataclasses import dataclass
import logging
import pint
from typing import Callable, Any

from .visitrecord import VisitRecord
from config import Configuration

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.FileHandler('operators.log', 'w+'))


@dataclass
class OpToken:
    op: str             # e.g. '+'
    pop: int            # precedence
    pleft: int          # left side precedence
    pright: int         # right side precedence
    expr_fmt: str       # e.g. '{left}+{right}'
    subs_fmt: str = ''  # optional subs format

    def __post_init__(self):
        if not self.subs_fmt:
            self.subs_fmt = self.expr_fmt


_C = Configuration()


OP_TOKENS:dict[type,OpToken] = {
    # Binary Operators
    ast.Add:        OpToken('+', 10, 10, 10, _C['expression.format.add']),
    ast.Sub:        OpToken('-', 10, 10, 15, _C['expression.format.sub']),
    ast.Mult:       OpToken('*', 20, 20, 20, _C['expression.format.mult']),
    ast.Div:        OpToken('/', 20, -1, -1, _C['expression.format.div']),
    ast.Mod:        OpToken('%', 20, 20, 25, _C['expression.format.modulo']),
    ast.Pow:        OpToken('^', 30, 30, -1, _C['expression.format.pow']),
    ast.MatMult:    OpToken('@', 20, 20, 20, _C['expression.format.matmult']),

    # Unary Operators
    ast.USub:       OpToken('-', 10, -1, 15, _C['expression.format.usub']),
    ast.UAdd:       OpToken('+', 10, -1, 10, _C['expression.format.uadd']),
    ast.Not:        OpToken('~', 10, -1, 15, _C['expression.format.not']),
    ast.Invert:     OpToken('~', 10, -1, 15, _C['expression.format.not']),
}


def custom_mult(token, left, right) -> OpToken:
    if isinstance(right.node, ast.Constant):
        token.expr_fmt = _C['expression.format.mult_constant']
        token.subs_fmt = _C['substituted.format.mult_constant']
    #TODO: Add support for pint units
    else:
        token.expr_fmt = _C['expression.format.mult']
        token.subs_fmt = _C['substituted.format.mult']
    return token


CUSTOM_TOKENS:dict[type, Callable] = {
    ast.Mult:       custom_mult,
}


def get_op_token(
        op:ast.BinOp|ast.UnaryOp,
        left:VisitRecord|None,
        right:VisitRecord|None
) -> tuple[OpToken|None,VisitRecord|None,VisitRecord|None]:
    """
    Retrieve the operator token for a given AST operation and apply custom
    formatting and precedence-based parenthesization to operands.

    Parameters
    ----------
    op : ast.BinOp | ast.UnaryOp
        The AST node representing a binary or unary operation.
    left : VisitRecord | None
        The VisitRecord for the left operand (None for unary operations).
    right : VisitRecord | None
        The VisitRecord for the right operand.

    Returns
    -------
    tuple[OpToken | None, VisitRecord | None, VisitRecord | None]
        A tuple containing:
        - The OpToken for the operation (or None if not found)
        - The potentially modified left operand VisitRecord (or None)
        - The potentially modified right operand VisitRecord (or None)
    """
    op_type = type(op.op)
    token = OP_TOKENS.get(op_type)
    custom_token_func = CUSTOM_TOKENS.get(op_type)

    if token and custom_token_func:
        token = custom_token_func(token, left, right)
    if token and left:
        left = parens_by_precedence(token.pleft, left)
    if token and right:
        right = parens_by_precedence(token.pright, right)
    return token, left, right


def transform_binop(xform:ast.NodeTransformer, node:ast.BinOp, namespace:dict[str,Any]) -> VisitRecord:
    """
    Transform a binary operation AST node into a VisitRecord with LaTeX representations.

    This function processes binary operations (e.g., addition, multiplication, division)
    by visiting the left and right operands, applying appropriate formatting based on
    operator precedence, and generating both expression and substituted LaTeX representations.
    Special handling is applied for pint quantities.

    Parameters
    ----------
    xform : ast.NodeTransformer
        The transformer instance used to visit child nodes.
    node : ast.BinOp
        The binary operation AST node to transform.
    namespace : dict[str, Any]
        The namespace dictionary containing variable definitions and values.

    Returns
    -------
    VisitRecord
    """
    record_out = VisitRecord(node=node)

    # Check if this is a pint unit
    if is_pint_quantity(node, namespace):
        return make_pint_quantity_record(record_out, namespace)

    # Process the operator
    token, left, right = get_op_token(node, xform.visit(node.left), xform.visit(node.right))

    if token and left and right:
        record_out.tex_expr = token.expr_fmt.format(left=left.tex_expr, right=right.tex_expr)
        record_out.tex_subs = token.subs_fmt.format(left=left.tex_subs, right=right.tex_subs)

    elif left and right:
        generic_out = f'\\texttt{{{node.op.__class__.__name__}}}({{{left.expr}}},{{{right.expr}}})'
        record_out.tex_expr = generic_out
        record_out.tex_subs = generic_out

    return record_out


def transform_unaryop(
        xform:ast.NodeTransformer,
        node:ast.UnaryOp,
        namespace:dict[str,Any]
) -> VisitRecord:
    """
    Transform a unary operation AST node into a VisitRecord with LaTeX representations.

    This function processes unary operations (e.g., negation, logical not)
    by visiting the operand, applying appropriate formatting based on
    operator precedence, and generating both expression and substituted LaTeX representations.
    Special handling is applied for pint quantities.

    Parameters
    ----------
    xform : ast.NodeTransformer
        The transformer instance used to visit child nodes.
    node : ast.UnaryOp
        The unary operation AST node to transform.
    namespace : dict[str, Any]
        The namespace dictionary containing variable definitions and values.

    Returns
    -------
    VisitRecord
    """
    record_out = VisitRecord(node=node)

    # Check if this is a pint unit
    if is_pint_quantity(node, namespace):
        return make_pint_quantity_record(record_out, namespace)

    token, _, operand = get_op_token(node, None, xform.visit(node.operand))
    
    if token and operand:
        record_out.tex_expr = token.expr_fmt.format(right=operand.tex_expr)
        record_out.tex_subs = token.subs_fmt.format(right=operand.tex_subs)

    elif operand:
        generic_out = f'\\texttt{{{node.op.__class__.__name__}}}({{{operand.expr}}})'
        record_out.tex_expr = generic_out
        record_out.tex_subs = generic_out

    return record_out


def parens_by_precedence(
        pop:int,
        record:VisitRecord,
) -> VisitRecord:
    """
    Adjusts the parentheses in the LaTeX expression of a syntax tree node based
    on operator precedence rules. This function ensures that the resulting LaTeX
    expression respects mathematical precedence by adding parentheses where
    necessary.

    Parameters
    ----------
    pop : int
        The precedence level of the current operator.
    record : VisitRecord
        An instance of ``VisitRecord`` containing information about
        the current node being visited, including its type and LaTeX representation.

    Returns
    -------
    VisitRecord
        Updated ``VisitRecord`` with potentially adjusted LaTeX expressions
        to reflect proper parenthetical grouping.
    """
    if isinstance(record.node, (ast.BinOp, ast.UnaryOp)):
        other_token = OP_TOKENS.get(type(record.node.op))
        if other_token and (pop > other_token.pop):
            record.tex_expr = f'\\left({{{record.tex_expr}}}\\right)'
            record.tex_subs = f'\\left({{{record.tex_subs}}}\\right)'
    return record


def is_pint_quantity(node:Any, namespace:dict) -> bool:
    """
    Check if an AST node represents a pint unit.

    Args:
        node: The AST node to check.
        namespace: The namespace dictionary containing variable definitions.

    Returns:
        True if the node represents a single pint quantity.
    """
    LOG.debug(f'\nISPQ:\n===============')

    if isinstance(node, ast.Name):
        return isinstance(namespace.get(node.id), pint.Unit)

    if isinstance(node, ast.BinOp):
        return (
            _first_nonunit_right_leaf_is_constant(node.left, namespace)
            and _all_leaves_are_units(node.right, namespace)
        )
    return False


def make_pint_quantity_record(record:VisitRecord, namespace:dict[str,Any]) -> VisitRecord:
    """
    Create a VisitRecord for a pint quantity node.

    Parameters
    ----------
    record : VisitRecord
    namespace : dict[str, Any]

    Returns
    -------
    VisitRecord
    """
    node_value = eval(record.expr, namespace)
    record.tex_expr = _C['expression.format.pint'].format(value=_C.reduce_units(node_value))
    record.tex_subs = _C['substituted.format.pint'].format(value=_C.reduce_units(node_value))
    return record


def _all_leaves_are_units(node:ast.AST, namespace:dict[str,Any]) -> bool:
    LOG.debug(f'\nALAU: {ast.dump(node, indent=2)}')
    if isinstance(node, ast.Name):
        return isinstance(namespace.get(node.id), pint.Unit)
    if isinstance(node, ast.Attribute):
        if isinstance(node.value, ast.Name):
            obj = namespace.get(node.value.id)
            if obj:
                attribute = getattr(obj, node.attr)
                if isinstance(attribute, pint.Unit):
                    return True
        return False
    if isinstance(node, ast.BinOp):
        return (_all_leaves_are_units(node.left, namespace)
                and _all_leaves_are_units(node.right, namespace))
    if isinstance(node, ast.UnaryOp):
        return _all_leaves_are_units(node.operand, namespace)
    return False


def _first_nonunit_right_leaf_is_constant(node:ast.AST, namespace:dict[str,Any]) -> bool:
    LOG.debug(f'\nFLIC: {ast.dump(node, indent=2)}')
    if isinstance(node, ast.Constant):
        return True

    if isinstance(node, ast.Name):
        return isinstance(namespace.get(node.id), pint.Unit)

    if isinstance(node, ast.BinOp):
        if isinstance(node.right, ast.Constant):
            return True

        if _all_leaves_are_units(node.right, namespace):
            return _first_nonunit_right_leaf_is_constant(node.left, namespace)

    if isinstance(node, ast.UnaryOp):
        return _first_nonunit_right_leaf_is_constant(node.operand, namespace)

    return False


__all__ = ['transform_binop', 'transform_unaryop']