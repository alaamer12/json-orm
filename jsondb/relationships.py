from typing import List, Optional, Type, TypeVar, Union, TYPE_CHECKING
from .exceptions import JsonDBError

if TYPE_CHECKING:
    from .model import Model

T = TypeVar("T", bound="Model")

class Relationship:
    def __init__(
        self,
        *,
        back_populates: Optional[str] = None,
        link_model: Optional[str] = None
    ):
        self.back_populates = back_populates
        self.link_model = link_model
        self.parent_model: Optional[Type[T]] = None
    
    def __set_name__(self, owner: Type[T], name: str) -> None:
        """Called when the relationship is defined in a model."""
        self.parent_model = owner
        self.name = name
    
    def __get__(self, instance: Optional[T], owner: Type[T]) -> Union[List[T], T, None]:
        """Get related records when accessing the relationship."""
        if instance is None:
            return self
        
        if not hasattr(instance, f"_{self.name}"):
            # Load related records
            if self.link_model:
                # Many-to-many relationship
                related = self._load_many_to_many(instance)
            else:
                # One-to-many or one-to-one relationship
                related = self._load_related(instance)
            
            setattr(instance, f"_{self.name}", related)
        
        return getattr(instance, f"_{self.name}")
    
    def _load_related(self, instance: T) -> Union[List[T], T, None]:
        """Load related records for one-to-one or one-to-many relationships."""
        if not self.parent_model:
            raise JsonDBError("Parent model not set")
        
        # Implementation details here
        pass
    
    def _load_many_to_many(self, instance: T) -> List[T]:
        """Load related records for many-to-many relationships."""
        if not self.parent_model or not self.link_model:
            raise JsonDBError("Parent model or link model not set")
        
        # Implementation details here
        pass

def relationship(
    *,
    back_populates: Optional[str] = None,
    link_model: Optional[str] = None
) -> Relationship:
    """Create a new relationship."""
    return Relationship(
        back_populates=back_populates,
        link_model=link_model
    )
