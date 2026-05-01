import pint
import yaml

from collections.abc import MutableMapping
from pathlib import Path
from typing import Any, cast, ClassVar

from ..protocols import FormatType

type FMT_REG = MutableMapping[type, FormatType]


class Configuration:
    """
    Configuration manager for ipycalcpad settings and unit preferences.

    This class implements a singleton class to load and manage configuration
    settings, handle object formatting and manage preferred units
    for display and conversion.

    Attributes
    ----------
    format_registry : Mapping[type, FormatType]
        Class-level registry mapping types to their formatters.
    """
    format_registry: ClassVar[FMT_REG]
    _config: ClassVar[dict[str,Any]]

    def __new__(cls, *args, **kwargs):
        """
        Create or return the singleton Configuration instance.
        """
        if (not hasattr(cls, '_config')) or (cls._config is None):
            cls._load_config()
        if (not hasattr(cls, 'format_registry')) or (cls.format_registry is None):
            cls.format_registry = dict()
        return super().__new__(cls)

    def __getitem__(self, key):
        """
        Get a configuration value using dictionary-style access. Defaults to ``None`` if key not found.
        """
        return self.get(key, default=None)

    @classmethod
    def get(cls, key:str, default=None) -> Any:
        """
        Get a configuration value with an optional default.

        Parameters
        ----------
        key : str
            The configuration key to retrieve, may use dot notation for nested values.
        default : Any, optional
            The value to return if the key is not found (default is None).

        Returns
        -------
        Any
            The configuration value associated with the key, or the default value if not found.
        """
        cfg = cls._get_deep_attribute(cls._config, key.strip())
        return cfg if cfg else default

    @staticmethod
    def reduce_units(value: Any) -> Any:...
    #NOTE: method is defined below.

    @classmethod
    def format_object(cls, obj: Any, format_spec:str=None) -> str:
        """
        Format an object using registered formatters.

        Parameters
        ----------
        obj : Any
            The object to format.
        format_spec : str, optional
            The format specification string (default is None).

        Returns
        -------
        str
            The formatted string representation of the object.

        Notes
        -----
        First looks up formatter by exact type match, then by subclass match.
        If no formatter is found, returns the object's string representation.
        """
        # first lookup by type.
        formatter = cls.format_registry.get(type(obj))
        if formatter:
            return formatter.format(obj, format_spec)

        # if not found, try by subclass.
        for _t, formatter in cls.format_registry.items():
            if isinstance(obj, _t):
                return formatter.format(obj, format_spec)

        # if none found return __str__.
        return str(obj)

    @classmethod
    def register_format(cls, obj_type: type, formatter: FormatType):
        """
        Register a formatter for a specific object type.

        Parameters
        ----------
        obj_type : type
            The type of object to register the formatter for.
        formatter : FormatType
            The formatter instance to use for the specified type.
        """
        cls.format_registry[obj_type] = formatter

    @classmethod
    def _load_config(cls):
        """
        Load configuration from the config.yaml file.

        Reads the YAML configuration file located in the same directory as this
        module and stores the parsed configuration in the class-level _config attribute.

        Raises
        ------
        FileNotFoundError
            If config.yaml is not found in the module directory
        yaml.YAMLError
            If the YAML file cannot be parsed

        Notes
        -----
        TODO: Allow the user to specify a config file that will override the default configs.
        """
        fil_path = Path(__file__).with_name('config.yaml')
        with open(fil_path, 'r') as fil:
            cls._config = yaml.safe_load(fil)

    @classmethod
    def _get_deep_attribute(cls, dct: dict[str, Any], key: str) -> Any | None:
        """
        Recursively retrieve a nested attribute from a dictionary using dot notation.

        Parameters
        ----------
        dct : dict[str, Any]
            The dictionary to search for the attribute
        key : str
            The dot-separated path to the desired attribute (e.g., 'level1.level2.level3')

        Returns
        -------
        Any | None
            - If the path leads to an object, returns the object
            - Returns None if the path is not found.
        """
        obj_name, op, attr_name = key.partition('.')
        obj = dct.get(obj_name)

        if obj and op:
            if isinstance(obj, dict):
                return cls._get_deep_attribute(obj, attr_name) if attr_name else None
            else:
                return None
        return obj


# Initialize the singleton instance.
_C = Configuration()
_PINT_PREFERRED_UNIT_STRS = cast(list[str], _C['objects.preferred_units'])
if _PINT_PREFERRED_UNIT_STRS:
    _PINT_PREFERRED_UNITS = [pint.Unit(i) for i in _PINT_PREFERRED_UNIT_STRS]
else:
    _PINT_PREFERRED_UNITS = None

# Define the ``reduce_units`` method. This is defined here so that the Configuration
# can be instantiated and used to import the preferred units.
def reduce_units(value: Any) -> Any:
    """
    Reduce units of a pint Quantity to preferred or base units.

    Parameters
    ----------
    value : Any
        The value to reduce. If not a pint.Quantity, returns unchanged.

    Returns
    -------
    Any
        If value is a pint.Quantity, returns the quantity converted to preferred
        units (if configured) or base units. Otherwise, returns the original value.
    """
    if not isinstance(value, pint.Quantity):
        return value

    if _PINT_PREFERRED_UNITS:
        return value.to_preferred(_PINT_PREFERRED_UNITS)
    else:
        return value.to_base_units()
Configuration.reduce_units = staticmethod(reduce_units)


__all__ = ['Configuration']
