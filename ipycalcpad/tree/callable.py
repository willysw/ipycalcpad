import ast

from collections.abc import Callable, Sequence, Mapping
from dataclasses import dataclass, KW_ONLY, field
from math import nan
from typing import Any, ClassVar

from ..protocols import NodeType
from .node import Node
from .terminals import PintQuantity
from ..utility import get_root_object, name_to_tex


from ..config import Configuration
_C = Configuration()

_TEMPLATE_KEY:str = 'callables.default'
_TEMPLATE_KEY_KNOWN:str = 'callables.known_function'
_SPECIAL_FUNCTIONS_KEY:str = 'callables.special_functions'
_KNOWN_FUNCTIONS_KEY:str = 'callables.known_functions'

@dataclass
class Func(Node):
    _:KW_ONLY
    name: str
    func: Callable
    arguments: Sequence[NodeType]
    child_fields: ClassVar[tuple[str, ...]] = ('func','arguments')
    func_template: str = field(default=_C[_TEMPLATE_KEY], repr=False)
    func_is_special: bool = field(default=False, repr=False)

    def __post_init__(self):
        if self.name in (fns:=self.special_functions):
            self.func_is_special = True
            self.func_template = fns[self.name]
        elif self.name in self.known_functions:
            self.func_template = _C[_TEMPLATE_KEY_KNOWN]

    @classmethod
    def from_ast(
            cls,
            node: ast.Call,
            namespace: Mapping[str, Any],
            children: Sequence[NodeType]
    ) -> 'Func|PintQuantity':
        # Special case for PintQuantity
        if isinstance(node.func, ast.Name) and node.func.id == '_PINT_':
            return PintQuantity.from_ast(node, namespace)

        func = get_root_object(node.func, namespace)
        if func and isinstance(func, Callable):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            else:
                func_name = func.__name__

            return Func(namespace,
                        name=func_name,
                        func=func,
                        arguments=children)
        else:
            raise NotImplementedError

    def get_tex(
            self,
            subs: bool = False,
            format_spec: str|None = None,
            preferred_units: Sequence[str]|None = None
    ) -> str:
        if self.func_is_special:
            return self.func_template.format(name=self.name,
                                             args=self.args_tex(subs=subs,
                                                                format_spec=format_spec,
                                                                preferred_units=preferred_units))
        else:
            return (self.func_template
                    .format(
                        name=name_to_tex(self.name),
                        args=self.all_args_tex(
                            subs=subs,
                            format_spec=format_spec,
                            preferred_units=preferred_units
                        )
                    ))

    @property
    def value(self) -> Any:
        return self.call()

    @property
    def special_functions(self) -> dict[str, str]:
        out = dict()
        if special := _C[_SPECIAL_FUNCTIONS_KEY]:
            out.update(special)
        return out

    @property
    def known_functions(self) -> set[str]:
        out = set()
        if known := _C[_KNOWN_FUNCTIONS_KEY]:
            out.update(known)
        return out

    def call(self) -> Any:
        if self.func:
            return getattr(self, 'func')(*self.args_values())
        else:
            return nan

    def args_tex(
            self,
            subs: bool = False,
            format_spec: str = None,
            preferred_units: Sequence[str] = None
    ) -> list[str]:
        return [arg.get_tex(subs=subs,
                            format_spec=format_spec,
                            preferred_units=preferred_units)
                for arg in self.arguments]

    def all_args_tex(
            self,
            subs: bool = False,
            format_spec: str = None,
            preferred_units: Sequence[str] = None
    ) -> str:
        return ', '.join(self.args_tex(subs=subs,
                                       format_spec=format_spec,
                                       preferred_units=preferred_units))

    def args_values(self) -> list[Any]:
        return [arg.value for arg in self.arguments]


__all__ = ['Func']
