"""
Line processing module for IPyCalcPad.

This module defines the Line class which represents a single line of
calculation expressions with optional comments. It handles parsing,
evaluation, and markdown rendering of mathematical expressions.
"""

from argparse import Namespace
from collections.abc import Sequence
from dataclasses import dataclass
from typing import cast

from ..protocols import NodeType
from ..tree import Assign, Literal

from ..config import Configuration
_C = Configuration()

_FULL_LINE_TEMPLATE:str = _C['line.full_line']
_FULL_EXPR_TEMPLATE:str = _C['line.full_expression']
_EXPR_SEP:str = _C['line.expression_separator']
_EXPRESSION_TEMPLATE:str = _C['line.expression']
_SUBSTITUTED_TEMPLATE:str = _C['line.substituted']
_RESULT_TEMPLATE:str = _C['line.result']
_COMMENT_TEMPLATE:str = _C['line.comment']


@dataclass(kw_only=True)
class Expression:
    expr: NodeType
    py_expr: str


@dataclass(kw_only=True)
class Line:
    """
    Represents a single line containing expressions and an optional comment.

    A Line processes one or more mathematical expressions, executes them,
    and provides formatted output for rendering in Jupyter notebooks.

    Attributes
    ----------
    expressions : Sequence[NodeType] | None, optional
        Sequence of parsed expression nodes to be evaluated and rendered.
        Defaults to None.
    arguments : Namespace | None, optional
        Configuration arguments controlling rendering behavior such as
        substitution display. Defaults to None (creates empty Namespace).
    comment : str, optional
        Optional comment text to be displayed alongside expressions.
        Defaults to empty string.
    """
    expressions: Sequence[Expression]|None = None
    arguments: Namespace|None = None
    comment: str = ""
    format_spec: str|None = None
    preferred_units: Sequence[str]|None = None

    def __post_init__(self):
        """
        Initialize Line after dataclass construction.
        """
        if self.arguments is None:
            self.arguments = Namespace()

        if (
            self.expressions
                and
            self.arguments
                and
            ('no_execute' in self.arguments)
                and
            (not self.arguments.no_execute)
        ):
            for expr in self.expressions:
                exec(expr.py_expr, cast(dict, expr.expr.namespace))

    def _repr_markdown_(self) -> str:
        """
        Generate markdown representation for Jupyter notebook display.

        This method is automatically called by Jupyter to render the
        Line object as formatted markdown output.

        Returns
        -------
        str
            Markdown-formatted string representation of the line.
        """
        return self.get_markdown()

    def get_markdown(self) -> str:
        """
        Generate complete markdown string for the line.

        Combines expressions and comments according to configured
        templates. If no expressions exist, returns only the comment.

        Returns
        -------
        str
            Markdown-formatted string with expressions and comment.
        """
        if self.expressions:
            return _FULL_LINE_TEMPLATE.format(
                comment=self.comment_string,
                full_expression=_EXPR_SEP.join(self.get_expr_strings()), # noqa
            )
        else:
            return self.comment_string

    def get_expr_strings(self) -> Sequence[str]|None:
        """
        Generate formatted strings for all expressions.

        Combines expression, substitution, and result strings for each
        expression according to the configured template.

        Returns
        -------
        Sequence[str] | None
            List of formatted expression strings, or None if no
            expressions exist.
        """
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
        """
        Get LaTeX-formatted expression strings without substitution.

        Returns
        -------
        Sequence[str] | None
            List of LaTeX strings representing expressions in their
            original form, or None if no expressions exist.
        """
        if self.expressions:
            return [_EXPRESSION_TEMPLATE
                    .format(
                        tex=expr.expr.get_tex(
                            subs=False,
                            format_spec=self.format_spec,
                            preferred_units=self.preferred_units
                        )
                    )
                    for expr in self.expressions]
        else:
            return None

    @property
    def subs_strings(self) -> Sequence[str]|None:
        """
        Get LaTeX-formatted substitution strings for expressions.

        Generates substituted forms showing variable values if
        substitution is enabled and expressions contain substitutable
        fields.

        Returns
        -------
        Sequence[str] | None
            List of LaTeX substitution strings (empty strings for
            expressions without substitutions), or None if no
            expressions exist.
        """
        if self.expressions:
            if self.arguments and self.arguments.substitute:
                do_subs = [expr.expr.has_substituted_fields for expr in self.expressions]
                out = []
                for expr, do_sub in zip(self.expressions, do_subs):
                    if do_sub:
                        out.append(
                            _SUBSTITUTED_TEMPLATE.format(
                                tex=expr.expr.get_tex(subs=True,
                                                      format_spec=self.format_spec,
                                                      preferred_units=self.preferred_units)
                            )
                        )
                    else:
                        out.append("")
                return out
            else:
                return ["" for _ in self.expressions]
        else:
            return None

    @property
    def result_strings(self) -> Sequence[str]|None:
        """
        Get LaTeX-formatted result strings for expressions.

        Generates result values for expressions, excluding literal
        values and assignments to literals which don't need result
        display.

        Returns
        -------
        Sequence[str] | None
            List of LaTeX result strings (empty strings for literal
            expressions), or None if no expressions exist.
        """
        if self.expressions:
            expr_is_literal = [(isinstance(expr.expr, Literal)
                                or
                                (isinstance(expr.expr, Assign) and
                                 isinstance(expr.expr.expression, Literal)))
                                for expr in self.expressions]
            out = []
            for expr, is_literal in zip(self.expressions, expr_is_literal):
                if is_literal:
                    out.append("")
                else:
                    out.append(
                        _RESULT_TEMPLATE
                        .format(
                            tex=expr.expr
                            .get_tex_result(
                                format_spec=self.format_spec,
                                preferred_units=self.preferred_units
                            )
                        )
                    )
            return out
        else:
            return None

    @property
    def comment_string(self) -> str:
        """
        Get formatted comment string.

        Returns
        -------
        str
            LaTeX-formatted comment string, or empty string if no
            comment exists.
        """
        if self.comment:
            return _COMMENT_TEMPLATE.format(tex=self.comment)
        else:
            return ''


__all__ = ['Line', 'Expression']
