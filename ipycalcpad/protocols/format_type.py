from typing import Protocol, runtime_checkable, Any, ClassVar


@runtime_checkable
class FormatType(Protocol):
    """Protocol for formats types in ipycalcpad."""
    types_to_format: ClassVar[tuple[type,...]]

    def __call__(self, value: str, format_spec:str=None) -> str:...

    @classmethod
    def format(cls, value: Any, format_spec:str=None) -> str:...

    @classmethod
    def register_format(cls) -> None:...


__all__ = ['FormatType']
