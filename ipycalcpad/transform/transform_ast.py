import ast

from argparse import Namespace
from collections.abc import Mapping
from typing import Any

from ..protocols import NodeType
from ..tree import Literal, Variable, Func, BinOp, UnaryOp, Assign, SequenceNode


class SkipLineException(Exception):
    pass


class ASTTransformer(ast.NodeTransformer):
    namespace: Mapping[str,Any]
    arguments: Namespace

    def __init__(self, namespace: Mapping[str,Any], arguments: Namespace):
        self.namespace = namespace
        self.arguments = arguments
        super().__init__()

    def generic_visit(self, node: ast.AST) -> NodeType:
        raise SkipLineException

    def visit_Module(self, node: ast.Module) -> list[NodeType]:
        lines_out = []
        for expr in node.body:
            try:
                lines_out.append(self.visit(expr))
            except SkipLineException:
                pass

        return lines_out

    def visit_Expr(self, node: ast.Expr) -> NodeType:
        return self.visit(node.value)

    def visit_Assign(self, node: ast.Assign) -> NodeType:
        return Assign.from_ast(
            node, self.namespace,
            children=(self.visit(node.targets[0]), self.visit(node.value))
        )

    def visit_Name(self, node: ast.Name) -> NodeType:
        return Variable.from_ast(node, self.namespace)

    def visit_Constant(self, node: ast.Constant) -> NodeType:
        return Literal.from_ast(node, self.namespace)

    def visit_Subscript(self, node: ast.Subscript) -> NodeType:
        key = self.visit(node.slice)
        return Variable.from_ast(node, self.namespace, children=(key,))

    def visit_Attribute(self, node: ast.Attribute) -> NodeType:
        return Variable.from_ast(node, self.namespace)

    def visit_Call(self, node: ast.Call) -> NodeType:
        arguments = [self.visit(arg) for arg in node.args]
        return Func.from_ast(node, self.namespace, children=arguments)

    def visit_BinOp(self, node: ast.BinOp) -> NodeType:
        left , right = self.visit(node.left), self.visit(node.right)
        return BinOp.from_ast(node, self.namespace, children=(left, right))

    def visit_UnaryOp(self, node: ast.UnaryOp) -> NodeType:
        operand = self.visit(node.operand)
        return UnaryOp.from_ast(node, self.namespace, children=(operand,))

    def visit_Tuple(self, node: ast.Tuple) -> NodeType:
        children = [self.visit(elt) for elt in node.elts]
        return SequenceNode.from_ast(node, self.namespace, children=children)

    def visit_List(self, node: ast.List) -> NodeType:
        children = [self.visit(elt) for elt in node.elts]
        return SequenceNode.from_ast(node, self.namespace, children=children)

    #TODO: implement these
    """ Unimplemented Visitors """
    def visit_Slice(self, node: ast.Slice) -> slice|None:
        raise NotImplementedError("Slice nodes are not supported yet in this transformer")

    def visit_Set(self, node: ast.Set) -> set[NodeType]:
        raise NotImplementedError("Set nodes are not supported yet in this transformer")

    def visit_Dict(self, node: ast.Dict) -> dict[NodeType, NodeType]:
        raise NotImplementedError("Dict nodes are not supported yet in this transformer")


__all__ = ['ASTTransformer']
