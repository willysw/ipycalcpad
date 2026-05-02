import ast
import pandas

from argparse import Namespace
from typing import Any, Mapping, Sequence

from ..protocols import NodeType
from ..tree import Assign, Variable
from .line import Line
from .long_line import LongLine
from ..transform import ASTTransformer, PintTransformer

__all__ = ['line_from_cell_line_text']

_LONG_LINE_TYPES = (pandas.DataFrame, pandas.Series)


def line_from_cell_line_text(
        line_text: str,
        namespace: Mapping[str, Any],
        arguments: Namespace
) -> Line:
    """
    Create Line objects from a line of Python code.

    Parses the input to create a Line or LongLine based on the
    expression type.

    Parameters
    ----------
    line_text : str
        The raw text of the line to parse.
    namespace : Mapping[str, Any]
        Dictionary of variable definitions for expression evaluation.
    arguments : Namespace
        Configuration arguments for rendering and substitution.

    Yields
    ------
    Line
        A Line or LongLine.
    """
    line_ast = ast.parse(line_text)
    line_comment = get_line_comment(line_text, line_ast)
    line_expressions = get_line_expressions(line_ast, namespace, arguments)

    if (line_expressions
            and
            isinstance(line_expressions[0], (Variable, Assign))
            and
            isinstance(line_expressions[0].value, _LONG_LINE_TYPES)):
        return LongLine(expressions=line_expressions,
                       comment=line_comment,
                       arguments=arguments)
    else:
        return Line(expressions=line_expressions,
                   comment=line_comment,
                   arguments=arguments)


def get_line_expressions(
        line_ast: ast.AST,
        namespace: Mapping[str,Any],
        arguments: Namespace
) -> Sequence[NodeType]|None:
    """
    Extract and transform expressions from a parsed AST.

    Applies Pint unit transformations and AST transformations to
    convert the parsed AST into NodeType objects.

    Parameters
    ----------
    line_ast : ast.AST
        The parsed AST tree of the line.
    namespace : Mapping[str, Any]
        Dictionary of variable definitions for expression evaluation.
    arguments : Namespace
        Configuration arguments for rendering and substitution.

    Returns
    -------
    Sequence[NodeType] or None
    """
    if isinstance(line_ast, ast.Module) and line_ast.body:
        line_pint_ast = PintTransformer(namespace).visit(line_ast)
        return ASTTransformer(namespace, arguments).visit(line_pint_ast)
    else:
        return None


def get_line_comment(
        line_text: str, 
        line_ast: ast.AST
) -> str:
    """
    Extract comment text from a line of code.

    Parameters
    ----------
    line_text : str
        The raw text of the line to extract comment from.
    line_ast : ast.AST
        The parsed AST tree of the line.

    Returns
    -------
    str
        The extracted comment text.
    """
    start_search_pos = get_line_comment_position(line_ast)
    raw_comment = line_text[start_search_pos:].partition('#')[2]
    #TODO: get extras here
    return raw_comment.strip()


def get_line_comment_position(
        line_ast: ast.AST
) -> int:
    """
    Determine the column position where a comment may start.

    Recursively traverses the AST to find the rightmost column
    offset of any node which indicates where code ends and a
    comment could begin.

    Parameters
    ----------
    line_ast : ast.AST
        The parsed AST tree of the line to analyze.

    Returns
    -------
    int
        The column offset after the last code element, or 0 if
        the tree is empty.
    """
    if isinstance(line_ast, ast.Module):
        if line_ast.body:
            return get_line_comment_position(line_ast.body[-1])

    end_offsets = [n.end_col_offset for n in ast.walk(line_ast)
                   if (hasattr(n, 'end_col_offset') and
                       n.end_col_offset is not None)]
    return max(end_offsets) if end_offsets else 0