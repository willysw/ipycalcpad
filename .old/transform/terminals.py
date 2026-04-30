import ast
import pint
from typing import Any

from .visitrecord import VisitRecord
from config import Configuration


_C = Configuration()


_SPECIAL_NAMES = {
    'pi': '\\pi',
    'alpha': '\\alpha', 'beta': '\\beta', 'gamma': '\\gamma', 'Gamma': '\\Gamma',
    'delta': '\\delta', "Delta": "\\Delta", 'epsilon': '\\epsilon',
    'zeta': '\\zeta', 'eta': '\\eta', 'theta': '\\theta', 'iota': '\\iota',
    'kappa': '\\kappa', 'lambda': '\\lambda', 'mu': '\\mu', 'nu': '\\nu',
    'xi': '\\xi', 'chi': '\\chi', 'omicron': '\\omicron',
    'omega': '\\omega', 'Omega': '\\Omega', 'upsilon': '\\upsilon',
    'sigma': '\\sigma', 'Sigma': '\\Sigma', 'phi': '\\phi'
}


def transform_name(
        xform:ast.NodeTransformer,
        node:ast.Name,
        namespace:dict[str,Any]
) -> VisitRecord:
    val = namespace.get(node.id)
    record_out = VisitRecord(node=node, expr=node.id)
    record_out.tex_expr = _process_parts(node.id)

    #TODO: move to separate function
    if isinstance(val, (pint.Unit, pint.Quantity)):
        record_out.tex_subs = _C['substituted.format.pint'].format(value=val)
    else:
        record_out.tex_subs = _C['substituted.format.default'].format(value=val)

    return record_out


def transform_attribute(
        xform:ast.NodeTransformer,
        node:ast.Attribute,
        namespace:dict[str,Any]
) -> VisitRecord: #TODO: add recursive attribute support
    python_expr = ast.unparse(node)
    python_value = eval(python_expr, namespace)
    return VisitRecord(
        node=node,
        expr=python_expr,
        tex_expr=str(python_value),
        tex_subs=str(python_value)
    )


def transform_constant(node:ast.Constant) -> VisitRecord:
    """
    Transform an AST Constant node into a VisitRecord with LaTeX representations.

    Parameters
    ----------
    node : ast.Constant

    Returns
    -------
    VisitRecord
    """
    return VisitRecord(
        node=node,
        expr=ast.unparse(node),
        tex_expr=_C['expression.format.default'].format(value=node.value),
        tex_subs=_C['substituted.format.default'].format(value=node.value)
    )


def _process_parts(raw_name:str) -> str:
    """
    Process a raw name by splitting it into parts and formatting it for LaTeX.
    """
    parts = raw_name.split('_')
    for i, part_i in enumerate(parts):
        if part_i in _SPECIAL_NAMES:
            parts[i] = _SPECIAL_NAMES[part_i]

    if len(parts) > 1:
        return f'{parts[0]}_{{{','.join(parts[1:])}}}'
    else:
        return parts[0]


__all__ = ['transform_name', 'transform_attribute', 'transform_constant']