import ast
from dataclasses import dataclass


@dataclass
class VisitRecord:
    node: ast.AST
    expr: str = ''
    assign: str = ''
    tex_expr: str = ''
    tex_subs: str = ''
    tex_assign: str = ''

    def __post_init__(self):
        if not self.expr: self.expr = ast.unparse(self.node)
        if not self.tex_expr: self.tex = f'{{{self.node}}}'


__all__ = ['VisitRecord']