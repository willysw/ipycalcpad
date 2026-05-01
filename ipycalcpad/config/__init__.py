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
from .formats.number_format import NumberFormat
from .formats.string_format import StringFormat
from .formats.pint_format import PintFormat
from .formats.pandas_format import PDDataFrameFormat, PDSeriesFormat

for _C in (NumberFormat, StringFormat, PintFormat, PDDataFrameFormat,
           PDSeriesFormat):
    _C.register_format()


__all__ = ['Configuration']
