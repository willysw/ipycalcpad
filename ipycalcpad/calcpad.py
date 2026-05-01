import ast
import pandas

from argparse import Namespace
from collections.abc import Sequence, Mapping
from dataclasses import dataclass, field, InitVar

from rich.pretty import pprint
from typing import Any

from .protocols import NodeType
from .tree import Assign, Variable
from .line import Line, LongLine
from .transform import ASTTransformer, PintTransformer

from .config import Configuration
_C = Configuration()

_CELL_START = _C['cell.start']
_CELL_END = _C['cell.end']


@dataclass(kw_only=True)
class CalcPad:
    """
    A calculation pad for processing and displaying mathematical expressions.

    Parses cell text containing Python expressions and provides markdown
    rendering for Jupyter notebooks.

    Parameters
    ----------
    cell_text : str
        The raw text content of a cell to be processed.
    namespace : Mapping[str, Any], optional
        The namespace containing variable definitions for evaluation.

    Attributes
    ----------
    lines : Sequence[Line]
        List of Line objects representing processed expressions.
    arguments : Mapping[str, Any]
        Configuration arguments for rendering and substitution.
    """
    cell_text: InitVar[str] = None
    namespace: InitVar[Mapping[str,Any]] = None
    lines: Sequence[Line] = field(default_factory=list)
    arguments: Namespace = field(default_factory=Namespace)

    #TODO: This class needs to be set up so that each line is frozen
    # once it has been transformed and executed.

    def __post_init__(self, cell_text: str, namespace: Mapping[str,Any]):
        self.init_from_string(cell_text, namespace)
        if self.arguments.debug:
            pprint(self.arguments, expand_all=True)
            pprint(self, expand_all=True)

    def init_from_string(
            self,
            cell_text: str = None,
            namespace: Mapping[str,Any] = None
    ) -> None:
        """
        Initialize CalcPad from raw cell text.
    
        Parses the input text line by line, applies transformations
        including Pint unit handling, and creates Line objects for each
        line with expressions and comments.
    
        Parameters
        ----------
        cell_text : str, optional
            The raw text content to be processed. If None, no
            initialization is performed.
        namespace : Mapping[str, Any], optional
            Dictionary of variable definitions for expression
            evaluation. Defaults to empty dict if cell_text is
            provided.
    
        Returns
        -------
        None
        """
        if cell_text:
            namespace = namespace if (namespace is not None) else {}
            self.lines = [line for line in self._yield_new_lines(cell_text, namespace, self.arguments)]
        else:
            self.lines = []

    def _yield_new_lines(self, cell_text:str, namespace:Mapping[str,Any], arguments:Namespace):
        for line_text in cell_text.splitlines():
            line_ast = ast.parse(line_text)
            line_comment = self._get_line_comment(line_text, line_ast)
            line_expressions = self._get_line_expressions(line_ast, namespace)

            #TODO: move this to a separate function in lines subpackage. This class
            # should not need to know about pandas nor which types trigger long lines.
            if (line_expressions
                    and
                isinstance(line_expressions[0], (Variable,Assign))
                    and
                isinstance(line_expressions[0].value, (pandas.DataFrame, pandas.Series))):
                    yield LongLine(expressions=line_expressions,
                                   comment=line_comment,
                                   arguments=arguments)
            else:
                yield Line(expressions=line_expressions,
                           comment=line_comment,
                           arguments=arguments)

    def _repr_markdown_(self):
        """
        Generate Markdown representation of the Calcpad cell.
        """
        if _CELL_START and _CELL_END: #TODO: this needs to change.
            return (
                _CELL_START +
                '\n\n' +
                '\n\n'.join(line.get_markdown() for line in self.lines) +
                '\n\n' +
                _CELL_END
            )
        else:
            return '\n\n'.join(line.get_markdown() for line in self.lines)

    #TODO: These functions should be moved to the lines subpackage.
    def _get_line_expressions(self, line_ast:ast.AST, namespace:Mapping[str,Any]) -> Sequence[NodeType]|None:
        if isinstance(line_ast, ast.Module) and line_ast.body:
            line_pint_ast = PintTransformer(namespace).visit(line_ast)
            return ASTTransformer(namespace, self.arguments).visit(line_pint_ast)
        else:
            return None

    def _get_line_comment(self, line_text: str, line_ast_tree:ast.AST) -> str:
        """
        Extract comment text from a line of code.

        Parameters
        ----------
        line_text : str
            The raw text of the line to extract comment from.
        line_ast_tree : ast.AST
            The parsed AST tree of the line.

        Returns
        -------
        str
            The extracted comment text with leading/trailing
            whitespace removed.
        """
        start_search_pos = self._get_line_comment_position(line_ast_tree)
        raw_comment = line_text[start_search_pos:].partition('#')[2]
        #TODO: get extras here
        return raw_comment.strip()

    def _get_line_comment_position(self, line_ast_tree: ast.AST) -> int:
        """
        Determine the column position where a comment may start.

        Recursively traverses the AST to find the rightmost column
        offset of any node, which indicates where code ends and a
        comment could begin.

        Parameters
        ----------
        line_ast_tree : ast.AST
            The parsed AST tree of the line to analyze.

        Returns
        -------
        int
            The column offset after the last code element, or 0 if
            the tree is empty.
        """
        if isinstance(line_ast_tree, ast.Module):
            if line_ast_tree.body:
                return self._get_line_comment_position(line_ast_tree.body[-1])

        end_offsets = [n.end_col_offset for n in ast.walk(line_ast_tree)
                       if (hasattr(n, 'end_col_offset') and
                           n.end_col_offset is not None)]
        return max(end_offsets) if end_offsets else 0


