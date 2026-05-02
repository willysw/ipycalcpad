from argparse import Namespace

from ..tree import Assign

from .line import Line


class LongLine(Line):
    """
    A line type for rendering long-form objects.

    Extends Line to provide detailed markdown output of an object with comments,
    variable descriptions, and formatted results suitable for
    multi-line display in Jupyter notebooks. Does not support substitutions
    nor execute the line.

    Attributes
    ----------
    arguments : Namespace
        Configuration arguments for rendering, inherited from Line.
    expressions : Sequence[NodeType]
        List of expression nodes to be rendered.
    comment : str
        Optional comment text associated with this line.
    """

    def __post_init__(self):
        """
        Initialize LongLine with default arguments if not provided.

        Sets arguments to an empty Namespace if None to ensure
        consistent attribute access during rendering.

        Returns
        -------
        None
        """
        if self.arguments is None:
            self.arguments = Namespace()

    def get_markdown(self):
        """
        Generate markdown representation for long-form display.

        Creates a multi-line markdown string containing:
        - Comment text (if present)
        - Assignment target description (if applicable)
        - Full TeX-formatted result with substitutions

        Returns
        -------
        str
            Markdown-formatted string with newlines separating
            sections. Returns empty string if no expressions exist.
        """
        if self.expressions:
            expr = self.expressions[0]

            if self.comment:
                comment_text = f'{self.comment}\n\n'
            else:
                comment_text = ''

            if isinstance(expr, Assign) and expr.target:
                desc_text = f'${expr.target.get_tex(subs=False)}$\n\n'
            else:
                desc_text = ''

            return ('\n\n' +
                    comment_text +
                    desc_text +
                    expr.get_tex_result() +
                    '\n\n')

        return ""


__all__ = ['LongLine']
