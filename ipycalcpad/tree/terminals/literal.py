import ast

from collections.abc import Sequence, Mapping
from dataclasses import dataclass, KW_ONLY
from typing import Any, ClassVar

from ...protocols import NodeType
from .terminal import Terminal

from ...config import Configuration
_C = Configuration()

_TEMPLATE:str = _C['literals.default']


@dataclass
class Literal(Terminal):
    _:KW_ONLY
    obj: Any = None
    template: ClassVar[str] = _TEMPLATE

    @classmethod
    def from_ast(
            cls,
            node: ast.expr,
            namespace: Mapping[str,Any],
            children: Sequence[NodeType] = None
    ) -> 'Literal':
        if isinstance(node, ast.Constant):
            return cls(node, namespace, obj=node.value)
        else:
            raise TypeError(f'Expected Constant, got {type(node)}') # noqa


__all__ = ['Literal']
