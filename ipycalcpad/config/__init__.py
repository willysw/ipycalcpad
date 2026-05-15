"""
Configuration management subpackage for ipycalcpad.

This subpackage provides configuration management functionality for ipycalcpad,
including settings, unit preferences, and object formatting.

Classes
-------
Configuration
    Core configuration manager implementing singleton pattern for application settings.

Format
    Base class for formatters used to customize object display and conversion.
"""

from .config import Configuration
_C = Configuration()

# Register standard formatters
from .formats import *

for fmt in (
    PDDataFrameFormat,
    PDSeriesFormat,
    PintFormat,
    NumberFormat,
    StringFormat,
    SequenceFormat,
    NDArrayFormat,
):
    fmt.register_format()


__all__ = ['Configuration']
