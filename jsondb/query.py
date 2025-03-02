from typing import Any, List, Optional, Type, TypeVar, Union
from .model import Model
from .conditions import Condition, and_, or_

T = TypeVar("T", bound=Model)

class QueryBuilder:
    def __init__(self, database: "Database", model_class: Type[T]):
        self.database = database
        self.model_class = model_class
        self.conditions: List[Condition] = []
        self.order_by_field: Optional[str] = None
        self.order_desc: bool = False
        self.limit_val: Optional[int] = None
        self.offset_val: Optional[int] = None
        self.joins: List[str] = []
    
    def where(self, condition: Condition) -> "QueryBuilder":
        """Add a where condition."""
        self.conditions.append(condition)
        return self
    
    def order_by(self, field: str, desc: bool = False) -> "QueryBuilder":
        """Add order by clause."""
        self.order_by_field = field
        self.order_desc = desc
        return self
    
    def limit(self, limit: int) -> "QueryBuilder":
        """Add limit clause."""
        self.limit_val = limit
        return self
    
    def offset(self, offset: int) -> "QueryBuilder":
        """Add offset clause."""
        self.offset_val = offset
        return self
    
    def join(self, model_class: Type[Model]) -> "QueryBuilder":
        """Add a join."""
        self.joins.append(model_class.__name__)
        return self
    
    def first(self) -> Optional[T]:
        """Get first result."""
        results = self.all()
        return results[0] if results else None
    
    def all(self) -> List[T]:
        """Execute query and get all results."""
        # Get all records
        records = self.database.chunk_manager.get_all_records(
            self.model_class.__name__
        )
        
        # Apply conditions
        if self.conditions:
            records = self._apply_conditions(records)
        
        # Apply order by
        if self.order_by_field:
            records = sorted(
                records,
                key=lambda x: x[self.order_by_field],
                reverse=self.order_desc
            )
        
        # Apply limit and offset
        if self.offset_val:
            records = records[self.offset_val:]
        if self.limit_val:
            records = records[:self.limit_val]
        
        # Convert to model instances
        return [self.model_class(**record) for record in records]
    
    def _apply_conditions(self, records: List[dict]) -> List[dict]:
        """Apply where conditions to records."""
        result = []
        for record in records:
            if all(condition.evaluate(record) for condition in self.conditions):
                result.append(record)
        return result

class UpdateBuilder:
    def __init__(self, database: "Database", model_class: Type[Model]):
        self.database = database
        self.model_class = model_class
        self.conditions: List[Condition] = []
        self.updates: dict = {}
    
    def where(self, condition: Condition) -> "UpdateBuilder":
        """Add a where condition."""
        self.conditions.append(condition)
        return self
    
    def values(self, **kwargs) -> "UpdateBuilder":
        """Set values to update."""
        self.updates.update(kwargs)
        return self
    
    def execute(self) -> int:
        """Execute update and return number of affected records."""
        # Implementation details here
        pass

class DeleteBuilder:
    def __init__(self, database: "Database", model_class: Type[Model]):
        self.database = database
        self.model_class = model_class
        self.conditions: List[Condition] = []
    
    def where(self, condition: Condition) -> "DeleteBuilder":
        """Add a where condition."""
        self.conditions.append(condition)
        return self
    
    def execute(self) -> int:
        """Execute delete and return number of affected records."""
        # Implementation details here
        pass

def select(model_class: Type[T]) -> QueryBuilder:
    """Create a select query."""
    from .database import Database
    return QueryBuilder(Database, model_class)

def update(model_class: Type[Model]) -> UpdateBuilder:
    """Create an update query."""
    from .database import Database
    return UpdateBuilder(Database, model_class)

def delete(model_class: Type[Model]) -> DeleteBuilder:
    """Create a delete query."""
    from .database import Database
    return DeleteBuilder(Database, model_class)
