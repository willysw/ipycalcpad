import ast

from collections.abc import Callable, Sequence, Mapping
from dataclasses import dataclass, KW_ONLY, field
from math import nan
from typing import Any, ClassVar

from ..protocols import NodeType
from .node import Node
from .terminals import PintQuantity


from ..config import Configuration
_C = Configuration()

_TEMPLATE:str = _C['callables.default']
_TEMPLATE_KNOWN:str = _C['callables.known_function']
_SPECIAL_FUNCTIONS:dict[str,str] = _C['callables.special_functions']
_KNOWN_FUNCTIONS:list[str] = _C['callables.known_functions']


@dataclass
class Func(Node):
    _:KW_ONLY
    name: str
    func: Callable
    arguments: Sequence[NodeType]
    child_fields: ClassVar[tuple[str, ...]] = ('func','arguments')
    func_template: str = field(default=_TEMPLATE, repr=False)
    func_is_special: bool = field(default=False, repr=False)

    def __post_init__(self):
        if self.name in _SPECIAL_FUNCTIONS:
            self.func_is_special = True
            self.func_template = _SPECIAL_FUNCTIONS[self.name]
        elif self.name in _KNOWN_FUNCTIONS:
            self.func_template = _TEMPLATE_KNOWN


    @classmethod
    def from_ast(
            cls,
            node: ast.Call,
            namespace: Mapping[str, Any],
            children: Sequence[NodeType]
    ) -> 'Func|PintQuantity':
        func_name = node.func.id
        # Special case for PintQuantity
        if func_name == '_PINT_':
            return PintQuantity.from_ast(node, namespace)

        func = namespace.get(func_name)
        if func and isinstance(func, Callable):
            return Func(node,
                        namespace,
                        name=func_name,
                        func=func,
                        arguments=children)
        else:
            raise EnvironmentError(f"Function {func_name} not found.")

    def get_tex(self, subs: bool = False) -> str:
        if self.func_is_special:
            return self.func_template.format(name=self.name, args=self.args_tex(subs))
        else:
            return self.func_template.format(name=self.name, args=self.all_args_tex(subs))

    @property
    def value(self) -> Any:
        return self.call()

    def call(self) -> Any:
        if self.func:
            return getattr(self, 'func')(*self.args_values())
        else:
            return nan

    def args_tex(self, subs: bool = False) -> list[str]:
        return [arg.get_tex(subs) for arg in self.arguments]

    def all_args_tex(self, subs: bool = False) -> str:
        return ', '.join(self.args_tex(subs))

    def args_values(self) -> list[Any]:
        return [arg.value for arg in self.arguments]


__all__ = ['Func']
