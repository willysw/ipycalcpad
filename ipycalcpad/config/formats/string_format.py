from ..format import Format

from ..config import Configuration
_C = Configuration()


class StringFormat(Format):
    types_to_format = (str,)

    @classmethod
    def format(cls, value: str, format_spec:str='') -> str:
        return str(value)


__all__ = ['StringFormat']
