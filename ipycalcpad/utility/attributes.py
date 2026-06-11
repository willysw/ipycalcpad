import ast

import builtins
from collections.abc import Mapping
from typing import Any


def get_attribute_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):  # Terminal
        return node.id

    if isinstance(node, ast.Attribute):
        return f"{get_attribute_name(node.value)}_{node.attr}"

    if isinstance(node, ast.Call):
        return f"{get_attribute_name(node.func)}"

    if isinstance(node, ast.Subscript):
        return f"{get_attribute_name(node.value)}"

    return ''


def get_root_object(
        node: ast.expr,
        namespace: Mapping[str, Any]
) -> Any:
    if isinstance(node, ast.Attribute):
        attr_name = node.attr
        root_object = get_root_object(node.value, namespace)
        if root_object:
            return getattr(root_object, attr_name)

    if isinstance(node, ast.Call):
        return get_root_object(node.func, namespace)

    if isinstance(node, ast.Name):
        if node.id in namespace:
            return namespace.get(node.id)
        elif hasattr(builtins, node.id):
            return getattr(builtins, node.id)

    return None


__all__ = ['get_root_object', 'get_attribute_name']
