import ast
import pandas

from argparse import Namespace
from typing import Any, Mapping, Sequence

from ..protocols import NodeType
from ..tree import Assign, Variable
from .line import Line, Expression
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

    # Extract the line comment
    line_comment = get_line_comment(line_text, line_ast)

    # Extract meta strings
    meta_strings = get_line_meta_strings(line_ast)
    format_spec, preferred_units = process_meta_strings(meta_strings)

    # Extract expressions after removing meta strings
    line_expressions = get_line_expressions(line_ast, namespace, arguments)

    if (line_expressions and
        isinstance(line_expressions[0].expr, (Variable, Assign)) and
        isinstance(line_expressions[0].expr.value, _LONG_LINE_TYPES)):
        return LongLine(expressions=line_expressions,
                        arguments=arguments,
                        comment=line_comment,
                        format_spec=format_spec,
                        preferred_units=preferred_units)
    else:
        return Line(expressions=line_expressions,
                    arguments=arguments,
                    comment=line_comment,
                    format_spec=format_spec,
                    preferred_units=preferred_units)


def get_line_expressions(
        line_ast: ast.AST,
        namespace: Mapping[str,Any],
        arguments: Namespace
) -> Sequence[Expression]|None:
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
        line_py_exprs = [ast.unparse(node) for node in line_ast.body]
        line_pint_ast = PintTransformer(namespace).visit(line_ast)
        line_expr_nodes = ASTTransformer(namespace, arguments).visit(line_pint_ast)
        return [Expression(expr=expr, py_expr=py_expr)
                for expr, py_expr
                in zip(line_expr_nodes, line_py_exprs)]
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


def get_line_meta_strings(line_ast:ast.AST) -> list[str]:
    """
    Extract meta strings from a line of code.
    """
    new_body = []
    meta_strings = []
    if isinstance(line_ast, ast.Module):
        for node in line_ast.body:
            if (isinstance(node, ast.Expr) and
                isinstance(node.value, ast.Constant) and
                isinstance(node.value.value, str)):
                meta_strings.append(node.value.value)
            else:
                new_body.append(node)
        line_ast.body = new_body
    return meta_strings


def process_meta_strings(meta_strings: list[str]) -> tuple[str|None, tuple[str]]:
    preferred_units = []
    format_spec = None
    for meta_string in meta_strings:
        for s in meta_string.strip().split():
            if s.startswith(':'):
                format_spec = s[1:]
            else:
                preferred_units.append(s)
    return format_spec, tuple(preferred_units)

