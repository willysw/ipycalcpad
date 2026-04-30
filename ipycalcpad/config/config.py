import pint
import yaml

from pathlib import Path
from typing import Any, cast

from ..protocols import NodeType


class Configuration:
    """
    Configuration manager for ipycalcpad settings and unit preferences.

    This class implements a singleton-like pattern to load and manage configuration
    settings from a YAML file, handle transform unit registry, and manage preferred units
    for display and conversion.
    """
    _config: dict[str,Any] = None

    def __new__(cls, *args, **kwargs):
        """
        Create or return the singleton Configuration instance.

        Returns
        -------
        Configuration
            A new Configuration instance with shared class-level configuration
        """
        if cls._config is None:
            cls._load_config()
        return super().__new__(cls)

    def __getitem__(self, key):
        """
        Get a configuration value using dictionary-style access.

        Defaults to ``None`` if ``key`` is not found.
        """
        return self.get(key, default=None)

    @classmethod
    def get(cls, key:str, default=None):
        """
        Get a configuration value with an optional default.
        """
        cfg = cls._get_deep_attribute(cls._config, key.strip())
        return cfg if cfg else default
    
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


################################
# ===== HELPER FUNCTIONS ===== #
################################

_C = Configuration()
_INTEGER_FORMAT = cast(str, _C['objects.integer'])
_DECIMAL_FORMAT = cast(str, _C['objects.decimal'])
_PINT_FORMAT = cast(str, _C['objects.pint_quantity'])
_PINT_PREFERRED_UNIT_STRS = cast(list[str], _C['objects.preferred_units'])
_PINT_PREFERRED_UNITS = [pint.Unit(i) for i in _PINT_PREFERRED_UNIT_STRS]


def reduce_units(value: Any) -> Any:
    if not isinstance(value, pint.Quantity):
        return value

    if _PINT_PREFERRED_UNITS:
        return value.to_preferred(_PINT_PREFERRED_UNITS)
    else:
        return value.to_base_units()


def format_object(obj:Any) -> str:
    if isinstance(obj, int):
        return _INTEGER_FORMAT.format(val=obj)

    elif isinstance(obj, float):
        return _DECIMAL_FORMAT.format(val=obj)

    elif isinstance(obj, pint.Quantity):
        return _PINT_FORMAT.format(val=reduce_units(obj))

    elif isinstance(obj, NodeType):
        return format_object(obj.get_result())

    else:
        return str(obj)