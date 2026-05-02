import ast

from collections.abc import Sequence, Mapping
from dataclasses import dataclass, KW_ONLY
from typing import ClassVar, Any, NamedTuple

from ...protocols import NodeType
from ...utility import name_to_tex
from .terminal import Terminal

from ...config import Configuration
_C = Configuration()

_TEMPLATE:str = _C['variables.default']
_TEMPLATE_SUBS:str = _C['variables.substituted']
_SPECIAL_VARS:dict[str,str] = _C['variables.special_vars']


class _AttrItem(NamedTuple):
    names: list[str]
    obj: Any
    @property
    def name(self):
        return "_".join(self.names)


KEY_TYPE = NodeType | str | int | slice | None


@dataclass
class Variable(Terminal):
    _:KW_ONLY
    name: str = ''
    key: KEY_TYPE = None
    template: ClassVar[str] = _TEMPLATE
    template_subs: ClassVar[str] = _TEMPLATE_SUBS

    @classmethod
    def from_ast(
            cls,
            node: ast.expr,
            namespace: Mapping[str,Any],
            children: Sequence[NodeType] = None
    ) -> NodeType:
        if isinstance(node, ast.Name):
            return cls(node, namespace, obj=namespace.get(node.id), name=node.id)

        elif isinstance(node, ast.Attribute):
            item = cls._get_attribute_names(node.value, namespace)
            return Variable(node, namespace, obj=item.obj, name=item.name)

        elif isinstance(node, ast.Subscript) and children:
            if isinstance(node.value, ast.Name):
                var = cls.from_ast(node.value, namespace)
                var.key=children[0]
                return var
            else:
                raise TypeError(f'Unexpected node type {type(node.value)} for subscripted variable')

        else:
            raise TypeError(f'Unexpected node type {type(node)} for variable') # noqa

    def get_tex(self, subs: bool = False) -> str:
        if subs and self.obj is not None:
            return self.template_subs.format(var=_C.format_object(self.obj))
        else:
            return self.template.format(var=name_to_tex(self.name, _SPECIAL_VARS))

    @property
    def has_substituted_fields(self) -> bool:
        if self.obj is not None:
            return True
        else:
            return False

    @classmethod
    def _get_attribute_names(cls, node: ast.AST, namespace: Mapping[str,Any]) -> _AttrItem:
        if isinstance(node, ast.Name):  # Terminal
            obj = namespace.get(node.id)
            if obj:
                return _AttrItem(names=[node.id], obj=obj)

        if isinstance(node, ast.Attribute):
            item = cls._get_attribute_names(node.value, namespace)
            if hasattr(item.obj, node.attr):
                return _AttrItem(names=item.names + [node.attr],
                                 obj=getattr(item.obj, node.attr))

        if isinstance(node, ast.Call):
            return _AttrItem(names=[node.func.id],
                             obj=eval(ast.unparse(node), namespace)) # noqa

        return _AttrItem(names=[], obj=eval(ast.unparse(node), namespace)) # noqa


__all__ = ['Variable', 'KEY_TYPE']
