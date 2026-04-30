import ast
from dataclasses import dataclass, field
import pint
from typing import Any

from .transformer import Transformer
from pint.transform_pint import PintTransformer
from .visitrecord import VisitRecord
from config import Configuration
_C = Configuration()


@dataclass
class TransformedLine:
    """
    A data container for transformed Python expressions into LaTeX representations.

    This class represents a single line of Python code that has been parsed and
    transformed into various LaTeX formatted representations. It stores both the
    original raw Python code and the generated LaTeX strings for assignments,
    expressions, substitutions, and comments.

    Attributes
    ----------
    assign : str
        LaTeX representation of the assignment target (left-hand side).
        Default is an empty string if no assignment is present.
    expression : str
        LaTeX representation of the expression (right-hand side or standalone).
        Default is an empty string.
    substituted : str
        LaTeX representation with substituted variable values.
        Default is an empty string.
    comment : str
        The comment text extracted from the raw line (after '#').
        Default is an empty string.
    namespace : dict[str, Any]
        The variable context dictionary used for expression evaluation.
        Not included in repr output.
    arguments : dict[str, Any]
        Optional arguments controlling transformation behavior.
        Not included in repr output.
    node : ast.AST
        The AST node resulting from parsing the raw line.
        Not included in repr output. None by default.
    raw_line : str
        The original unparsed input line.
    raw_expr : str
        The raw Python expression string (without comments).
    raw_assign : str
        The raw Python assignment target string.
    is_comment_only : bool
        Flag indicating whether the line contains only a comment.

    Properties
    ----------
    value : str
        Evaluates the raw expression and returns a formatted string representation.
        Handles both pint units/quantities and regular Python values.

    Methods
    -------
    from_raw(raw_line, namespace, arguments)
        Class method to create a TransformedLine from a raw input string.

    Notes
    -----
    This class is typically instantiated via the `from_raw` class method rather
    than direct construction. The transformation process uses the Transformer
    class to walk the AST and generate LaTeX representations.

    See Also
    --------
    Transformer : The AST transformer that generates LaTeX representations.
    VisitRecord : The record type used during AST transformation.
    """
    assign: str = field(default='')
    expression: str = field(default='')
    substituted: str = field(default='')
    comment: str = field(default='')
    namespace: dict[str,Any] = field(default_factory=dict, repr=False)
    arguments: dict[str,Any] = field(default_factory=dict, repr=False)
    node: ast.AST = field(default=None, repr=False)
    raw_line: str = field(default='', repr=False)
    raw_expr: str = field(default='', repr=False)
    raw_assign: str = field(default='', repr=False)
    is_comment_only: bool = field(default=False, repr=False)

    @property
    def value(self):
        value = eval(self.raw_expr, self.namespace)
        if isinstance(value, (pint.Quantity, pint.Unit)):
            return (
                _C['result.format.pint']
                .format(value=_C.reduce_units(value))
            )
        else:
            return _C['result.format.default'].format(value=value)

    @classmethod
    def from_raw(cls, *,
                 raw_line:str,
                 namespace:dict[str,Any],
                 arguments:dict[str,Any]):
        """
        Creates a new TransformedLine by parsing and processing a raw input line.

        Parameters
        ----------
        raw_line : str
            The raw string to be parsed of the form [assign =] expression [# comment] or [# comment].
        namespace : Namespace | Mapping[str, Any]
            A mapping or `Namespace` object containing the variable context
            for expression evaluation.
        arguments : Namespace | Mapping[str, Any]
            A mapping or `Namespace` object containing optional arguments.

        Returns
        -------
        TransformedLine
        """
        expression, _, comment = raw_line.partition('#')
        tree = ast.parse(expression)
        if tree.body:
            ptree = PintTransformer(namespace=namespace).visit(tree.body[0])
            record: VisitRecord = Transformer(namespace=namespace,
                                              arguments=arguments).visit(ptree)
            return cls(
                assign=record.tex_assign,
                expression=record.tex_expr,
                substituted=record.tex_subs,
                comment=comment.strip(),
                namespace=namespace,
                arguments=arguments,
                node=record.node,
                raw_line=raw_line.strip(),
                raw_expr=record.expr,
                raw_assign=record.assign,
            )
        else:
            return cls(
                comment=comment.strip(),
                namespace=namespace,
                arguments=arguments,
                raw_line=raw_line.strip(),
                is_comment_only=True,
            )


__all__ = ['TransformedLine']