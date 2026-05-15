import ast
from collections.abc import Sequence
from dataclasses import dataclass
from numpy import ndarray, asarray
from typing import Any, ClassVar, Mapping

from ..protocols import NodeType
from .node import Node
from .terminals.literals import SequenceLiteral, ArrayLiteral

_SEQ_FORMAT = "\\left[ {data} \\right]"


@dataclass(kw_only=True)
class SequenceNode(Node):
    elements: tuple[NodeType, ...] = None
    child_fields: ClassVar[tuple[str, ...]] = ('elements',)

    @classmethod
    def from_ast(
            cls,
            node: ast.Tuple|ast.List,
            namespace: Mapping[str,Any],
            children: Sequence[NodeType]
    ) -> NodeType:
        # if the ast elements are all constant, return a literal.
        if cls.are_all_elements_constant(node.elts):
            element_values = cls.reduce_ast_to_tuple(node.elts)
            element_types = cls.get_element_types(element_values)

            # if the element values are all of the same type and the
            # dimensions are homogeneous, return an ArrayLiteral
            if len(element_types) == 1:
                try:
                    return ArrayLiteral(namespace, obj=asarray(element_values))
                except ValueError:
                    # Raised on heterogeneous dimensionality. Ignore and continue.
                    pass

            # Otherwise return a SequenceLiteral
            return SequenceLiteral(namespace, obj=element_values)

        # Otherwise, return a SequenceNode
        return cls(namespace, elements=tuple(children))

    def get_tex(
            self,
            subs: bool = False,
            format_spec: str = None,
            preferred_units: Sequence[str] = None
    ) -> str:
        return _SEQ_FORMAT.format(
            data=' ,\\; '.join(e.get_tex(subs, format_spec, preferred_units) for e in self.elements),
        )

    def get_tex_result(
            self,
            format_spec: str = None,
            preferred_units: Sequence[str] = None
    ) -> str:
        return _SEQ_FORMAT.format(
            data=' ,\\; '.join(e.get_tex_result(format_spec, preferred_units) for e in self.elements),
        )

    def get_result(
            self,
            preferred_units: Sequence[str] = None
    ) -> tuple[Any,...]:
        return tuple(n.get_result(preferred_units) for n in self.elements)

    @property
    def value(self) -> Any:
        return tuple(n.value for n in self.elements)

    @classmethod
    def are_all_elements_constant(cls, elements: Sequence[ast.expr]) -> bool:
        elem_checks = []
        for el in elements:
            if isinstance(el, ast.Constant):
                elem_checks.append(True)
            elif isinstance(el, (ast.Tuple|ast.List)):
                elem_checks.append(cls.are_all_elements_constant(el.elts))
            else:
                return False
        return all(elem_checks)

    @classmethod
    def reduce_ast_to_tuple(cls, elements: Sequence[ast.expr]) -> tuple[Any, ...]:
        elem_values = []
        for el in elements:
            if isinstance(el, ast.Constant):
                elem_values.append(el.value)
            elif isinstance(el, (ast.Tuple|ast.List)):
                elem_values.append(cls.reduce_ast_to_tuple(el.elts))
        return tuple(elem_values)

    @classmethod
    def get_element_types(cls, elements: Sequence) -> set[type]:
        elem_types = set()
        for el in elements:
            if isinstance(el, Sequence):
                elem_types.update(cls.get_element_types(el))
            else:
                elem_types.add(type(el))
        return elem_types