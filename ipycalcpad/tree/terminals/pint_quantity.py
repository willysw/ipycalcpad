import ast
import pint

from collections.abc import Sequence, Mapping
from dataclasses import dataclass
from typing import Any

from ...protocols import NodeType
from .literal import Literal

from ...config import Configuration
_C = Configuration()


@dataclass
class PintQuantity(Literal):
    obj: 'pint.Quantity' = None

    def __post_init__(self):
        self.obj = _C.reduce_units(self.obj)

    @classmethod
    def from_ast(
            cls,
            node:ast.Call,
            namespace:Mapping[str,Any],
            children:Sequence[NodeType] = None,
    ) -> 'PintQuantity':
        args = [leaf.value for leaf in node.args if isinstance(leaf, ast.Constant)]
        kwargs = {kw.arg: kw.value.value
                  for kw in node.keywords
                  if isinstance(kw.value, ast.Constant)}
        return cls(node, namespace,
                   obj=(cls._get_registry(namespace)
                        .Quantity(*args, **kwargs))) # noqa

    @staticmethod
    def _get_registry(namespace:Mapping[str,Any]) -> pint.UnitRegistry:
        try:
            return next(obj for obj in namespace.values()
                        if isinstance(obj, pint.UnitRegistry))
        except StopIteration:
            raise EnvironmentError('No transform unit registry found in namespace')