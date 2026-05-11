import ast
import pint

from collections.abc import Sequence, Mapping
from dataclasses import dataclass
from typing import Any

from ....protocols import NodeType
from ..literal import Literal

from ....config import Configuration
_C = Configuration()


@dataclass
class PintQuantity(Literal):
    obj: 'pint.Quantity' = None

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
        return cls(namespace, obj=(_C.pint_registry.Quantity(*args, **kwargs))) # noqa
