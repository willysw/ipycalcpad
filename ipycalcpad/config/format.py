from typing import Any, ClassVar

from ..protocols import FormatType

from ..config import Configuration
_C = Configuration()

class Format(FormatType):
    types_to_format: ClassVar[tuple[type,...]]

    def __call__(self, value: str, format_spec:str=None) -> str:
        return self.format(value, format_spec)

    @classmethod
    def format(cls, value: Any, format_spec:str=None) -> str:
        raise NotImplementedError

    @classmethod
    def register_format(cls) -> None:
        for _T in cls.types_to_format:
            _C.register_format(_T, cls)


__all__ = ['Format']
