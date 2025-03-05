"""SQL expression system for JSON database with SQLModel compatibility.

This module provides a type-safe SQL expression system that mirrors SQLAlchemy's expression
language while working with JSON storage. It supports complex queries, relationships,
and common SQL operations while maintaining type safety and security.
"""

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, List, Optional, Union


class ExpressionType(Enum):
    """Types of SQL expressions supported by the system."""
    COLUMN = auto()
    LITERAL = auto()
    FUNCTION = auto()
    OPERATOR = auto()
    SUBQUERY = auto()


class ExpressionMixin:
    """Mixin providing security features for SQL expressions.
    
    Provides validation and sanitization methods to prevent SQL injection
    and ensure data integrity when working with JSON storage.
    """

    SAFE_IDENTIFIER = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

    @staticmethod
    def validate_identifier(name: str, type_name: str = "identifier") -> None:
        """Validate an SQL identifier for security.
        
        Args:
            name: The identifier to validate
            type_name: Type of identifier for error messages
            
        Raises:
            ValueError: If identifier contains unsafe characters
        """
        pass

    @staticmethod
    def sanitize_value(value: Any) -> Any:
        """Sanitize a literal value for safe storage.
        
        Args:
            value: Value to sanitize
            
        Returns:
            Sanitized value safe for JSON storage
        """
        pass


@dataclass
class Expression:
    """Base class for all SQL expressions with operator overloading.
    
    Provides Python operator overloading to enable SQLModel-like query syntax:
    ```python
    User.age > 18  # Creates a BinaryOperator expression
    ```
    """
    type: ExpressionType

    def __eq__(self, other: Any) -> 'BinaryOperator':
        """Create a BinaryOperator expression for equality."""
        return BinaryOperator(self, "=", other)

    def __ne__(self, other: Any) -> 'BinaryOperator':
        """Create a BinaryOperator expression for inequality."""
        return BinaryOperator(self, "!=", other)

    def __gt__(self, other: Any) -> 'BinaryOperator':
        """Create a BinaryOperator expression for greater than."""
        return BinaryOperator(self, ">", other)

    def __lt__(self, other: Any) -> 'BinaryOperator':
        """Create a BinaryOperator expression for less than."""
        return BinaryOperator(self, "<", other)

    def __ge__(self, other: Any) -> 'BinaryOperator':
        """Create a BinaryOperator expression for greater than or equal."""
        return BinaryOperator(self, ">=", other)

    def __le__(self, other: Any) -> 'BinaryOperator':
        """Create a BinaryOperator expression for less than or equal."""
        return BinaryOperator(self, "<=", other)


@dataclass
class Column(Expression, ExpressionMixin):
    """Represents a column in a SQL statement.
    
    Provides a type-safe way to reference columns in a table.
    """
    name: str
    table: Optional['Table'] = None
    alias: Optional[str] = None

    def __init__(self, name: str, table: Optional['Table'] = None, alias: Optional[str] = None):
        pass


@dataclass
class Table(ExpressionMixin):
    """Represents a table in a SQL statement.
    
    Provides a type-safe way to reference tables in a database.
    """
    name: str
    alias: Optional[str] = None

    def __init__(self, name: str, alias: Optional[str] = None): pass


@dataclass
class Literal(Expression, ExpressionMixin):
    """Represents a literal value in a SQL statement.
    
    Provides a type-safe way to include literal values in a query.
    """
    value: Any

    def __init__(self, value: Any):
        pass


@dataclass
class Function(Expression, ExpressionMixin):
    """Represents a function call in a SQL statement.
    
    Provides a type-safe way to include function calls in a query.
    """
    name: str
    arguments: List[Expression]

    def __init__(self, name: str, *args: Expression):
        pass


@dataclass
class BinaryOperator(Expression):
    """Represents a binary operator in a SQL statement.
    
    Provides a type-safe way to include binary operators in a query.
    """
    left: Expression
    operator: str
    right: Union[Expression, Any]

    def __init__(self, left: Expression, operator: str, right: Union[Expression, Any]):
        super().__init__(ExpressionType.OPERATOR)
        if operator not in {'=', '!=', '<', '<=', '>', '>=', 'AND', 'OR', '+', '-', '*', '/'}:
            raise ValueError(f"Invalid operator: {operator}")
        self.left = left
        self.operator = operator
        self.right = right if isinstance(right, Expression) else Literal(right)


@dataclass
class UnaryOperator(Expression):
    """Represents a unary operator in a SQL statement.
    
    Provides a type-safe way to include unary operators in a query.
    """
    operator: str
    operand: Expression

    def __init__(self, operator: str, operand: Expression):
        super().__init__(ExpressionType.OPERATOR)
        if operator not in {'NOT', '-', '+'}:
            raise ValueError(f"Invalid operator: {operator}")
        self.operator = operator
        self.operand = operand


# Common SQL functions
def count(expr: Expression) -> Function:
    """Create a COUNT function call."""
    return Function("COUNT", expr)


def sum_(expr: Expression) -> Function:
    """Create a SUM function call."""
    return Function("SUM", expr)


def avg(expr: Expression) -> Function:
    """Create an AVG function call."""
    return Function("AVG", expr)


def min_(expr: Expression) -> Function:
    """Create a MIN function call."""
    return Function("MIN", expr)


def max_(expr: Expression) -> Function:
    """Create a MAX function call."""
    return Function("MAX", expr)
