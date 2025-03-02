from dataclasses import dataclass
from typing import Any, Optional, Type, TypeVar, get_type_hints, List

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

    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        # Get type hints
        hints = get_type_hints(namespace)

        # Process fields
        fields = {}
        for key, hint in hints.items():
            if key in namespace and isinstance(namespace[key], Field):
                field = namespace[key]
                field.type = hint
                fields[key] = field

        # Store fields in class
        namespace['__fields__'] = fields

        return super().__new__(mcs, name, bases, namespace)


class Model(metaclass=ModelMeta):
    """Base class for all models."""

    def __init__(self, **kwargs):
        for name, field in self.__fields__.items():
            if name in kwargs:
                setattr(self, name, kwargs[name])
            elif field.default_factory is not None:
                setattr(self, name, field.default_factory())
            else:
                setattr(self, name, field.default)

    @classmethod
    def get_field(cls, name: str) -> Optional[Field]:
        """Get field by name."""
        return cls.__fields__.get(name)

    @classmethod
    def get_primary_key(cls) -> Optional[Field]:
        """Get primary key field."""
        for field in cls.__fields__.values():
            if field.primary_key:
                return field
        return None

    @classmethod
    def get_foreign_keys(cls) -> List[Field]:
        """Get all foreign key fields."""
        return [
            field for field in cls.__fields__.values()
            if field.foreign_key is not None
        ]

    @classmethod
    def get_indexes(cls) -> List[Field]:
        """Get all indexed fields."""
        return [
            field for field in cls.__fields__.values()
            if field.index
        ]

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            name: getattr(self, name)
            for name in self.__fields__
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Model':
        """Create model from dictionary."""
        return cls(**data)
