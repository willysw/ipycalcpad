from .config import Configuration
from .magic import Magic
from .transform import PintTransformer, ASTTransformer
from .line import Line
from .calcpad import CalcPad


def load_ipython_extension(ipython):
    ipython.register_magics(Magic)


__all__ = [
    'Configuration',
    'ASTTransformer',
    'PintTransformer',
    'Magic',
    'Line',
    'CalcPad',
]
