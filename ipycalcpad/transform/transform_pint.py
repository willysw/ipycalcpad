import ast
import pint

from collections.abc import Mapping
from typing import NamedTuple, Any


class NodeCheck(NamedTuple):
    node: ast.AST = None
    constant: ast.Constant = None

    def __bool__(self):
        return self.constant is not None

    def replace_leaf(self, node: ast.expr):
        if self and self.node:
            if isinstance(self.node, ast.BinOp): self.node.right = node
            if isinstance(self.node, ast.UnaryOp): self.node.operand = node


class PintTransformer(ast.NodeTransformer):
    namespace: Mapping[str,Any] = dict()

    def __init__(self, namespace: Mapping[str,Any]):
        self.namespace = namespace
        super().__init__()

    def visit_BinOp(self, node: ast.expr):
        # walk left node until a Constant node is found
        check = self._visit_left(node)
        if check:
            if isinstance(check.node, ast.Constant):
                return self._make_unit_node(node)
            else:
                check.replace_leaf(self._make_unit_node(node))
                return check.node
        else:
            node.left = self.visit(node.left)
            node.right = self.visit(node.right)
            return node

    def visit_UnaryOp(self, node: ast.expr):
        operand = self.visit(node.operand)
        if isinstance(operand, ast.Call) and operand.func.id == "Quantity":
            return self._make_unit_node(node)
        else:
            node.operand = operand
            return node

    def _visit_left(self, node: ast.expr) -> NodeCheck:
        if isinstance(node, ast.BinOp) and self._all_leaves_are_units(node.right):
            check = self._check_endpoint(node.left)
            if check:
                node.left = check.constant  # splits the tree
                return check
            else:
                # recurse left branch
                return self._visit_left(node.left)

        if isinstance(node, ast.UnaryOp):
            check = self._check_endpoint(node.operand)
            if check:
                node.operand = check.constant  # splits the tree
                return check
            else:
                return self._visit_left(node.operand)

        return NodeCheck()

    @staticmethod
    def _check_endpoint(node: ast.expr) -> NodeCheck:
        if isinstance(node, ast.Constant):
            return NodeCheck(node=node, constant=node)

        if isinstance(node, ast.BinOp) and isinstance(node.right, ast.Constant):
            return NodeCheck(node=node, constant=node.right)

        if isinstance(node, ast.UnaryOp) and isinstance(node.operand, ast.Constant):
            return NodeCheck(node=node, constant=node.operand)

        return NodeCheck()

    def _make_unit_node(self, node: ast.AST) -> ast.Call:
        quantity = eval(ast.unparse(node), self.namespace) # noqa
        return ast.Call(
            func=ast.Name(id='_PINT_', ctx=ast.Load()),
            args=[
                ast.Constant(quantity.magnitude),
                ast.Constant(str(quantity.units)),
            ],
        )

    def _all_leaves_are_units(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Name):
            return isinstance(self.namespace.get(node.id), pint.Unit)

        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            obj = self.namespace.get(node.value.id)
            if obj:
                attribute = getattr(obj, node.attr)
                if isinstance(attribute, pint.Unit):
                    return True
            return False

        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Pow):
                return self._all_leaves_are_units(node.left)
            else:
                return (
                        self._all_leaves_are_units(node.left) and
                        self._all_leaves_are_units(node.right)
                )

        if isinstance(node, ast.UnaryOp):
            return self._all_leaves_are_units(node.operand)

        return False


__all__=['PintTransformer']