import ast
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Mapping, Any

from ....protocols import NodeType
from ..literal import Literal


@dataclass
class SequenceNode(Literal):
    obj: Sequence = None

    @classmethod
    def from_ast(
            cls,
            node: ast.Tuple|ast.List,
            namespace: Mapping[str,Any],
            children: Sequence[NodeType] = None
    ) -> 'SequenceNode':
        if children:
            return cls(namespace, obj=children)
        else:
            return cls(namespace, obj=[])



