from argparse import Namespace
from collections.abc import Sequence
from dataclasses import dataclass

from .protocols import NodeType
from .tree import Terminal, Assign

from .config import Configuration
_C = Configuration()

_FULL_LINE_TEMPLATE:str = _C['line.full_line']
_FULL_EXPR_TEMPLATE:str = _C['line.full_expression']
_EXPR_SEP:str = _C['line.expression_separator']
_EXPRESSION_TEMPLATE:str = _C['line.expression']
_SUBSTITUTED_TEMPLATE:str = _C['line.substituted']
_RESULT_TEMPLATE:str = _C['line.result']
_COMMENT_TEMPLATE:str = _C['line.comment']


@dataclass(kw_only=True)
class Line:
    expressions: Sequence[NodeType]|None = None
    arguments: Namespace|None = None
    comment: str = ""

    def _repr_markdown_(self) -> str:
        return self.get_markdown()

    def get_markdown(self) -> str:
        if self.expressions:
            return _FULL_LINE_TEMPLATE.format(
                comment=self.comment_string,
                full_expression=_EXPR_SEP.join(self.get_expr_strings()), # noqa
            )
        else:
            return self.comment_string

    def get_expr_strings(self) -> Sequence[str]|None:
        if self.expressions:
            return [
                _FULL_EXPR_TEMPLATE.format(expression=expr,
                                           substituted=subs,
                                           result=res)
                for expr, subs, res
                in zip(self.expr_strings, self.subs_strings, self.result_strings) # noqa
            ]
        else:
            return None

    @property
    def expr_strings(self) -> Sequence[str]|None:
        if self.expressions:
         return [_EXPRESSION_TEMPLATE.format(tex=expr.get_tex(subs=False)) for expr in self.expressions]
        else:
            return None

    @property
    def subs_strings(self) -> Sequence[str]|None:
        if self.expressions:
            if self.arguments and self.arguments.substitute:
                do_subs = [expr.has_substituted_fields for expr in self.expressions]
                return [(_SUBSTITUTED_TEMPLATE.format(tex=expr.get_tex(subs=True))
                         if subs else "")
                        for expr, subs in zip(self.expressions, do_subs)]
            else:
                return ["" for _ in self.expressions]
        else:
            return None

    @property
    def result_strings(self) -> Sequence[str]|None:
        if self.expressions:
            expr_is_terminal = ((isinstance(expr, Terminal)
                                or
                                (isinstance(expr, Assign) and
                                 isinstance(expr.expression, Terminal)))
                                for expr in self.expressions)

            return [(_RESULT_TEMPLATE.format(tex=expr.get_tex_result())
                     if not is_terminal else "")
                    for expr, is_terminal
                    in zip(self.expressions, expr_is_terminal)]
        else:
            return None

    @property
    def comment_string(self) -> str:
        if self.comment:
            return _COMMENT_TEMPLATE.format(tex=self.comment)
        else:
            return ''


__all__ = ['Line']
