from dataclasses import dataclass
from typing import Any, Optional, Type, TypeVar

T = TypeVar('T')


@dataclass
class Field:
    """Field definition for models."""
    default: Any = None
    default_factory: Any = None
    primary_key: bool = False
    unique: bool = False
    index: bool = False
    foreign_key: Optional[str] = None

    def __set_name__(self, owner: Type[Any], name: str):
        self.name = name
        self.owner = owner


class ModelMeta(type):
    """Metaclass for Model to handle field definitions."""