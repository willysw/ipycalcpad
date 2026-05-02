"""
Line processing module for ipycalcpad.

This module provides classes and factory functions for representing and processing
individual lines of mathematical expressions in calculation pads. It handles both
standard and long-form expressions, converting AST nodes into structured Line objects
that can be rendered as LaTeX/Markdown.

Classes
-------
Line
    Base representation of a processed calculation line with expression, substitution,
    and result components.
LongLine
    Extended line representation for multi-part expressions with additional formatting.

Functions
---------
line_from_ast
    Factory function that creates appropriate Line objects from Python AST nodes
    and namespace context.

Examples
--------
>>> from argparse import Namespace
>>> the_line = line_from_cell_line_text("x = 5 + 3", namespace=locals(), arguments=Namespace())
>>> the_line.get_markdown()
"""
from .line import Line
from .long_line import LongLine
from .line_from_ast import line_from_cell_line_text

__all__ = ['Line', 'LongLine', 'line_from_cell_line_text']
