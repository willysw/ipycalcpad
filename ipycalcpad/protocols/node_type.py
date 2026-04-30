import ast

from collections.abc import Sequence, Mapping
from typing import Protocol, Any, ClassVar, runtime_checkable

@runtime_checkable
class NodeType(Protocol):
    ast_node: ast.AST
    namespace: Mapping[str,Any]
    node_precedence: ClassVar[int]
    child_fields: ClassVar[tuple[str, ...]]

    @classmethod
    def from_ast(cls,
                 node: ast.expr,
                 namespace: Mapping[str,Any],
                 children: Sequence['NodeType']) -> 'NodeType':...

    def get_tex(self, subs: bool = False) -> str:...

    def get_tex_result(self) -> str:...

    def get_result(self) -> Any:...

    @property
    def value(self) -> Any:...

    @property
    def text(self) -> str:...

    @property
    def has_substituted_fields(self) -> bool:...

    @staticmethod
    def parens_by_precedence(precedence: int,
                             other: 'NodeType',
                             subs: bool = False) -> str:...

    @staticmethod
    def name_to_tex(raw_name: str,
                    special_names: Mapping[str,str] = None) -> str:...


__all__ = ['NodeType']
