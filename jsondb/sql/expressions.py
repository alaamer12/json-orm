import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, List, Optional, Union


class ExpressionType(Enum):
    COLUMN = auto()
    LITERAL = auto()
    FUNCTION = auto()
    OPERATOR = auto()
    SUBQUERY = auto()


class ExpressionMixin:
    """Mixin providing security features for expressions."""

    # Regex for safe identifiers
    SAFE_IDENTIFIER = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

    @staticmethod
    def validate_identifier(name: str, type_name: str = "identifier") -> None:
        """Validate an SQL identifier."""
        if not ExpressionMixin.SAFE_IDENTIFIER.match(name):
            raise ValueError(f"Invalid {type_name}: {name}")

    @staticmethod
    def sanitize_value(value: Any) -> Any:
        """Sanitize a literal value."""
        if isinstance(value, str):
            # Remove null bytes and escape special chars
            value = value.replace('\0', '')
            value = value.replace("'", "''")
            value = value.replace("\\", "\\\\")
        elif isinstance(value, (int, float, bool, datetime)):
            # These types are safe as-is
            pass
        elif value is None:
            # None is safe
            pass
        else:
            raise ValueError(f"Unsupported literal type: {type(value)}")
        return value


@dataclass
class Expression:
    """Base class for all SQL expressions."""
    type: ExpressionType

    def __eq__(self, other: Any) -> 'BinaryOperator':
        return BinaryOperator(self, "=", other)

    def __ne__(self, other: Any) -> 'BinaryOperator':
        return BinaryOperator(self, "!=", other)

    def __gt__(self, other: Any) -> 'BinaryOperator':
        return BinaryOperator(self, ">", other)

    def __lt__(self, other: Any) -> 'BinaryOperator':
        return BinaryOperator(self, "<", other)

    def __ge__(self, other: Any) -> 'BinaryOperator':
        return BinaryOperator(self, ">=", other)

    def __le__(self, other: Any) -> 'BinaryOperator':
        return BinaryOperator(self, "<=", other)


@dataclass
class Column(Expression, ExpressionMixin):
    """Represents a column in a SQL statement."""
    name: str
    table: Optional['Table'] = None
    alias: Optional[str] = None

    def __init__(self, name: str, table: Optional['Table'] = None, alias: Optional[str] = None):
        super().__init__(ExpressionType.COLUMN)
        self.validate_identifier(name, "column name")
        if table and isinstance(table, str):
            self.validate_identifier(table, "table name")
        self.name = name
        self.table = table
        if alias:
            self.validate_identifier(alias, "alias")
            self.alias = alias


@dataclass
class Table(ExpressionMixin):
    """Represents a table in a SQL statement."""
    name: str
    alias: Optional[str] = None

    def __init__(self, name: str, alias: Optional[str] = None):
        self.validate_identifier(name, "table name")
        self.name = name
        if alias:
            self.validate_identifier(alias, "alias")
            self.alias = alias


@dataclass
class Literal(Expression, ExpressionMixin):
    """Represents a literal value in a SQL statement."""
    value: Any

    def __init__(self, value: Any):
        super().__init__(ExpressionType.LITERAL)
        self.value = self.sanitize_value(value)


@dataclass
class Function(Expression, ExpressionMixin):
    """Represents a function call in a SQL statement."""
    name: str
    arguments: List[Expression]

    def __init__(self, name: str, *args: Expression):
        super().__init__(ExpressionType.FUNCTION)
        self.validate_identifier(name, "function name")
        self.name = name
        self.arguments = list(args)


@dataclass
class BinaryOperator(Expression):
    """Represents a binary operator in a SQL statement."""
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
    """Represents a unary operator in a SQL statement."""
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
    return Function("COUNT", expr)


def sum_(expr: Expression) -> Function:
    return Function("SUM", expr)


def avg(expr: Expression) -> Function:
    return Function("AVG", expr)


def min_(expr: Expression) -> Function:
    return Function("MIN", expr)


def max_(expr: Expression) -> Function:
    return Function("MAX", expr)
