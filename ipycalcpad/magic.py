from argparse import ArgumentParser
from rich.pretty import install
install()

from IPython import get_ipython # noqa
_IPYTHON = get_ipython()

from IPython.display import display
from IPython.core.magic import Magics, magics_class, line_cell_magic

from .calcpad import CalcPad

_PARSER = ArgumentParser(prog='calcpad', add_help=True)

_RENDER_GROUP = _PARSER.add_argument_group('Rendering Options')
_RENDER_GROUP.add_argument('-s', '--substitute',
                           action='store_true',
                           help='Substitute variables in the expression')
_RENDER_GROUP.add_argument('-nx', '--no-execute',
                           action='store_true',
                           help='Do not execute the python code.')

_UTIL_GROUP = _PARSER.add_argument_group('Utilities')
_UTIL_GROUP.add_argument('--debug',
                         action='store_true',
                         help='Show debug information.')

@magics_class
class Magic(Magics):

    @line_cell_magic
    def calcpad(self, line:str, cell:str) -> CalcPad|None:
        try:
            arguments = _PARSER.parse_args(line.split())
        except SystemExit:
            return None

        return CalcPad(cell_text=cell, arguments=arguments, namespace=_IPYTHON.user_ns)
