import ast

from collections.abc import Sequence, Mapping
from dataclasses import dataclass, KW_ONLY
from typing import Any, ClassVar

from ..protocols import NodeType
from .node import Node

from ..config import Configuration
_C = Configuration()

_TEMPLATE:str = _C['assign.default']
_TEMPLATE_SUBS:str = _C['assign.substituted']


@dataclass
class Assign(Node):
    """
    Represents an assignment statement in the computation tree.

    This node stores an assignment operation with a target variable
    and an expression that evaluates to the assigned value.

    Attributes
    ----------
    target : NodeType
        The node representing the assignment target (variable name).
    expression : NodeType
        The node representing the expression being assigned.
    """
    _:KW_ONLY
    target: NodeType = None
    expression: NodeType = None
    child_fields: ClassVar[tuple[str, ...]] = ('target', 'expression')
    
    @classmethod
    def from_ast(
            cls,
            node: ast.Assign,
            namespace: Mapping[str,Any],
            children: Sequence[NodeType]
    ) -> NodeType:
        """
        Create an Assign node from an AST assignment node.

        Parameters
        ----------
        node : ast.Assign
            The AST assignment node to convert.
        namespace : Mapping[str, Any]
            Variable namespace for resolution.
        children : Sequence[NodeType]
            Child nodes where the first is the target and the second
            is the expression.

        Returns
        -------
        NodeType
            A new Assign instance.
        """
        return cls(node, namespace, target=children[0], expression=children[1])
    
    def get_tex(self, subs: bool = False) -> str:
        if subs:
            return _TEMPLATE_SUBS.format(target=self.target.get_tex(False),
                                         val=self.expression.get_tex(True))
        else:
            return _TEMPLATE.format(target=self.target.get_tex(False),
                                    val=self.expression.get_tex(False))
    
    @property
    def value(self):
        return self.expression.value

    
__all__ = ['Assign']

