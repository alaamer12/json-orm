from typing import Any, Callable, Dict, List, Optional, Union
import operator
from datetime import datetime

class Condition:
    def __init__(
        self,
        field: str,
        op: Callable[[Any, Any], bool],
        value: Any
    ):
        self.field = field
        self.op = op
        self.value = value
    
    def evaluate(self, record: Dict) -> bool:
        """Evaluate condition against a record."""
        if self.field not in record:
            return False
        
        record_value = record[self.field]
        
        # Handle datetime comparisons
        if isinstance(self.value, datetime) and isinstance(record_value, str):
            record_value = datetime.fromisoformat(record_value)
        
        return self.op(record_value, self.value)

class CompoundCondition:
    def __init__(self, conditions: List[Condition], op: Callable[[List[bool]], bool]):
        self.conditions = conditions
        self.op = op
    
    def evaluate(self, record: Dict) -> bool:
        """Evaluate compound condition against a record."""
        results = [cond.evaluate(record) for cond in self.conditions]
        return self.op(results)

def and_(*conditions: Union[Condition, "CompoundCondition"]) -> CompoundCondition:
    """Create an AND condition."""
    return CompoundCondition(list(conditions), all)

def or_(*conditions: Union[Condition, "CompoundCondition"]) -> CompoundCondition:
    """Create an OR condition."""
    return CompoundCondition(list(conditions), any)

def not_(condition: Union[Condition, CompoundCondition]) -> CompoundCondition:
    """Create a NOT condition."""
    return CompoundCondition([condition], lambda x: not any(x))

# Comparison operators
def eq(field: str, value: Any) -> Condition:
    """Create an equals condition."""
    return Condition(field, operator.eq, value)

def ne(field: str, value: Any) -> Condition:
    """Create a not equals condition."""
    return Condition(field, operator.ne, value)

def gt(field: str, value: Any) -> Condition:
    """Create a greater than condition."""
    return Condition(field, operator.gt, value)

def ge(field: str, value: Any) -> Condition:
    """Create a greater than or equals condition."""
    return Condition(field, operator.ge, value)

def lt(field: str, value: Any) -> Condition:
    """Create a less than condition."""
    return Condition(field, operator.lt, value)

def le(field: str, value: Any) -> Condition:
    """Create a less than or equals condition."""
    return Condition(field, operator.le, value)

def like(field: str, pattern: str) -> Condition:
    """Create a LIKE condition."""
    def like_op(value: str, pattern: str) -> bool:
        import re
        pattern = pattern.replace("%", ".*")
        return bool(re.match(pattern, value))
    
    return Condition(field, like_op, pattern)

def in_(field: str, values: List[Any]) -> Condition:
    """Create an IN condition."""
    return Condition(field, lambda x, y: x in y, values)

def is_null(field: str) -> Condition:
    """Create an IS NULL condition."""
    return Condition(field, lambda x, y: x is None, None)

def is_not_null(field: str) -> Condition:
    """Create an IS NOT NULL condition."""
    return Condition(field, lambda x, y: x is not None, None)
