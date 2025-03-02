from typing import Any, Dict, Optional, Type, TypeVar, get_type_hints
from pydantic import BaseModel, Field as PydanticField
from datetime import datetime

class Field(PydanticField):
    def __init__(
        self,
        *,
        primary_key: bool = False,
        index: bool = False,
        unique: bool = False,
        foreign_key: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.primary_key = primary_key
        self.index = index
        self.unique = unique
        self.foreign_key = foreign_key

class ModelMetaclass(type):
    def __new__(cls, name: str, bases: tuple, namespace: dict):
        # Get all Field attributes
        fields = {}
        for key, value in namespace.items():
            if isinstance(value, Field):
                fields[key] = value
        
        # Store fields in class
        namespace["__fields__"] = fields
        
        # Create class
        return super().__new__(cls, name, bases, namespace)

class Model(BaseModel, metaclass=ModelMetaclass):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True
    
    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """Convert model to dictionary."""
        data = super().dict(*args, **kwargs)
        # Convert datetime to ISO format
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data
    
    @classmethod
    def get_primary_key(cls) -> str:
        """Get primary key field name."""
        for name, field in cls.__fields__.items():
            if field.primary_key:
                return name
        return "id"  # Default primary key
    
    @classmethod
    def get_indexes(cls) -> Dict[str, Field]:
        """Get all indexed fields."""
        return {
            name: field 
            for name, field in cls.__fields__.items() 
            if field.index or field.primary_key or field.unique
        }
    
    @classmethod
    def get_relationships(cls) -> Dict[str, "Relationship"]:
        """Get all relationships."""
        from .relationships import Relationship
        return {
            name: field
            for name, field in cls.__dict__.items()
            if isinstance(field, Relationship)
        }
