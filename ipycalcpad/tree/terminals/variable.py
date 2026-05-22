import ast

from collections.abc import Sequence, Mapping
from dataclasses import dataclass, KW_ONLY
from typing import ClassVar, Any

from ...protocols import NodeType
from ...utility import get_attribute_name, get_root_object, name_to_tex
from .terminal import Terminal

from ...config import Configuration
_C = Configuration()

_SPECIAL_VARS_KEY: str = 'variables.special_vars'

KEY_TYPE = NodeType | str | int | slice | None


@dataclass
class Variable(Terminal):
    _:KW_ONLY
    name: str = ''
    key: KEY_TYPE = None
    template_key: ClassVar[str] = 'variables.default'
    template_key_subs: ClassVar[str] = 'variables.substituted'

    @classmethod
    def from_ast(
            cls,
            node: ast.expr,
            namespace: Mapping[str,Any],
            children: Sequence[NodeType]|None = None
    ) -> NodeType:
        if isinstance(node, ast.Name):
            return cls(namespace, obj=namespace.get(node.id), name=node.id)

        elif isinstance(node, ast.Attribute):
            item_name = get_attribute_name(node)
            item_obj = get_root_object(node, namespace)
            return cls(namespace, obj=item_obj, name=item_name)

        elif isinstance(node, ast.Subscript) and children:
            if isinstance(node.value, ast.Name):
                var = cls.from_ast(node.value, namespace)
                var.key=children[0]
                return var
            else:
                raise TypeError(f'Unexpected node type {type(node.value)} for subscripted variable') # noqa

        else:
            raise TypeError(f'Unexpected node type {type(node)} for variable') # noqa

    @property
    def value(self) -> Any:
        if self.key is not None:
            if isinstance(self.key, NodeType):
                key = self.key.value
            elif isinstance(self.key, (slice | int | str)):
                key = self.key
            else:
                raise TypeError(f'Unexpected key type {self.key}: {type(self.key)}')

            if isinstance(self.obj, Mapping):
                return self.obj.get(key)

            if isinstance(self.obj, Sequence) and isinstance(key, (int, slice)):
                return self.obj.__getitem__(key) # noqa

        return super().value

    def get_tex(
            self,
            subs: bool = False,
            format_spec: str|None = None,
            preferred_units: Sequence[str]|None = None
    ) -> str:
        if not subs:
            return self.template.format(var=name_to_tex(self.name, self.special_vars))
        else:
            reduced_obj = _C.reduce_units(self.obj, preferred_units=preferred_units)
            return self.template_subs.format(
                var=_C.format_object(reduced_obj, format_spec=format_spec)
            )

    @property
    def template(self) -> str:
        return _C[self.template_key]

    @property
    def template_subs(self) -> str:
        return _C[self.template_key_subs]

    @property
    def special_vars(self) -> dict[str, str]:
        out = dict()
        if special:=_C[_SPECIAL_VARS_KEY]:
            out.update(special)
        return out

    @property
    def has_substituted_fields(self) -> bool:
        if self.obj is not None:
            return True
        else:
            return False


__all__ = ['Variable', 'KEY_TYPE']
