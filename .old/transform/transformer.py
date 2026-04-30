import ast
from typing import Any

from .visitrecord import VisitRecord
from config import Configuration

from .operators import transform_binop, transform_unaryop
from .callable import transform_call
from .terminals import transform_name, transform_attribute, transform_constant


_C = Configuration()


class Transformer(ast.NodeTransformer):
    """
    AST NodeTransformer that converts Python expressions to LaTeX representations.

    This transformer walks through Python abstract syntax tree (AST) nodes and
    generates corresponding LaTeX formatted strings suitable for mathematical
    display in Jupyter notebooks. It handles assignments, expressions, binary
    operations, unary operations, function calls, and various terminal nodes.

    Attributes
    ----------
    namespace : dict[str, Any]
        A dictionary containing the variable context for expression evaluation.
        Used to resolve variable names and their values during transformation.
    arguments : dict[str, Any]
        A dictionary containing optional arguments that control transformation
        behavior (e.g., substitution flags).

    Notes
    -----
    This class extends `ast.NodeTransformer` and returns `VisitRecord` objects
    containing both the original AST node and its LaTeX representations. The
    transformation supports pint units and special mathematical symbols.

    See Also
    --------
    VisitRecord : The record type returned by visitor methods.
    TransformedLine : The high-level API for transforming complete lines.
    """
    namespace:dict[str,Any]
    arguments:dict[str,Any]

    def __init__(self, *args,
                 namespace:dict[str,Any],
                 arguments:dict[str,Any],
                 **kwargs):
        self.namespace = namespace
        self.arguments = arguments
        super().__init__(*args, **kwargs)

    def generic_visit(self, node): return VisitRecord(node)

    def visit_Assign(self, node):
        return VisitRecord(
            node=node,
            expr=ast.unparse(node.value),
            assign=self.visit(node.targets[0]).expr,
            tex_assign=f'{self.visit(node.targets[0]).tex_expr}',
            tex_expr=f'{self.visit(node.value).tex_expr}',
            tex_subs=f'{self.visit(node.value).tex_subs}'
        )

    def visit_Expr(self, node):
        return VisitRecord(
            node=node,
            expr=ast.unparse(node.value),
            tex_expr=f'{self.visit(node.value).tex_expr}',
            tex_subs=f'{self.visit(node.value).tex_subs}'
        )

    def visit_Constant(self, node): return transform_constant(node)
    def visit_Attribute(self, node): return transform_attribute(self, node, self.namespace)
    def visit_Name(self, node):return transform_name(self, node, self.namespace)
    def visit_Call(self, node): return transform_call(self, node, self.namespace)
    def visit_BinOp(self, node): return transform_binop(self, node, self.namespace)
    def visit_UnaryOp(self, node): return transform_unaryop(self, node, self.namespace)


__all__ = ['Transformer']