from argparse import Namespace
from collections.abc import Sequence, Mapping
from dataclasses import dataclass, field, InitVar

from rich.pretty import pprint
from typing import Any

from .line import Line, line_from_cell_line_text

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
            self.lines = [line_from_cell_line_text(line_text=line_text,
                                                   namespace=namespace,
                                                   arguments=self.arguments)
                          for line_text in cell_text.splitlines()]
        else:
            self.lines = []

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

