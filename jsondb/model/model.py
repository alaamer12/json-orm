"""A zero-configuration JSON database with SQLModel compatibility.

This module provides the core model system for defining database schemas using Python classes.
It follows SQLModel/SQLAlchemy patterns for familiarity and easy migration paths.
"""

from dataclasses import dataclass
from typing import Any, Optional, Type, TypeVar

T = TypeVar('T')


@dataclass
class Field:
    """Field definition for model attributes with SQLModel-compatible behavior.
    
    This class defines the schema and constraints for model fields, supporting features like:
    - Default values and factories
    - Primary key designation
    - Unique constraints
    - Indexing
    - Foreign key relationships
    
    Args:
        default: Default value for the field
        default_factory: Callable that provides default value
        primary_key (bool): Whether this field is the primary key
        unique (bool): Whether this field must have unique values
        index (bool): Whether to create an index for this field
        foreign_key (str, optional): Reference to another table's field (format: "table.field")
    
    Example:
        ```python
        class User(Model):
            id: int = Field(primary_key=True)
            name: str = Field(unique=True)
            age: int = Field(default=0)
        ```
    """
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
    """Metaclass for Model to handle field definitions and provide ORM-like behavior.
    
    This metaclass processes field definitions during class creation to:
    - Register fields and their constraints
    - Set up relationships between models
    - Create necessary indexes
    - Validate schema definitions
    
    It enables SQLModel-like syntax while storing data in JSON format.
    """