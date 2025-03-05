from dataclasses import dataclass

from .interfaces import (
    IExpressionVisitor,
    IColumn, ILiteral, IOperator
)


@dataclass
class Column(IColumn):
    """Column reference expression."""


@dataclass
class Literal(ILiteral):
    """Literal value expression."""


@dataclass
class BinaryOperator(IOperator):
    """Binary operator expression."""


@dataclass
class UnaryOperator(IOperator):
    """Unary operator expression."""


class ExpressionBuilder:
    """Builder for SQL expressions."""


class ExpressionEvaluator(IExpressionVisitor):
    """Evaluates expressions against a row of data."""