import ast
from typing import Any

from .visitrecord import VisitRecord
from config import Configuration


_C = Configuration()


_SPECIAL_FUNCTIONS = {
    'sqrt': '\\sqrt{{{expr[0]}}}',
    'exp': 'e^{{{expr[0]}}}',
    'pow': '\\left({{{expr[0]}}}\\right)^{{{expr[1]}}}',
    'abs': '\\left|{expr[0]}\\right|',
}

_KNOWN_FUNCTIONS = {
    'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'sinh', 'cosh',
    'tanh', 'asinh', 'acosh', 'atanh', 'ln', 'log'
}


def transform_call(
        xform:ast.NodeTransformer,
        node:ast.Call,
        namespace:dict[str,Any]
) -> VisitRecord:
    func_name = xform.visit(node.func).expr
    arg_records = [xform.visit(arg) for arg in node.args]
    arg_exps = [arg_record.tex_expr for arg_record in arg_records]
    arg_subs = [arg_record.tex_subs for arg_record in arg_records]

    if func_name in _SPECIAL_FUNCTIONS:
        return VisitRecord(
            node=node,
            expr=ast.unparse(node),
            tex_expr=_SPECIAL_FUNCTIONS[func_name].format(expr=arg_exps),
            tex_subs=_SPECIAL_FUNCTIONS[func_name].format(expr=arg_subs)
        )
    elif func_name in _KNOWN_FUNCTIONS:
        return VisitRecord(
            node=node,
            expr=ast.unparse(node),
            tex_expr=f'\\{func_name}\\left({{{','.join(arg_exps)}}}\\right)',
            tex_subs=f'\\{func_name}\\left({{{','.join(arg_subs)}}}\\right)'
        )
    else:
        return VisitRecord(
            node=node,
            expr=ast.unparse(node),
            tex_expr=f'\\texttt{{{func_name}}}({",".join(arg_exps)})',
            tex_subs=f'\\texttt{{{func_name}}}({",".join(arg_subs)})'
        )


__all__ = ['transform_call']