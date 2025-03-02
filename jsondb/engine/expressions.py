from dataclasses import dataclass
from typing import Any, List, Optional, Dict

from .interfaces import (
    IExpression, IExpressionVisitor,
    IColumn, ILiteral, IFunction, IOperator
)


@dataclass
class Column(IColumn):
    """Column reference expression."""
    table: str
    name: str
    alias: Optional[str] = None

    def accept(self, visitor: IExpressionVisitor) -> Any:
        return visitor.visit_column(self)


@dataclass
class Literal(ILiteral):
    """Literal value expression."""
    value: Any
    type_: type

    def accept(self, visitor: IExpressionVisitor) -> Any:
        return visitor.visit_literal(self)


@dataclass
class Function(IFunction):
    """Function call expression."""
    name: str
    args: List[IExpression]
    distinct: bool = False

    def accept(self, visitor: IExpressionVisitor) -> Any:
        return visitor.visit_function(self)


@dataclass
class BinaryOperator(IOperator):
    """Binary operator expression."""
    left: IExpression
    operator: str
    right: IExpression

    def accept(self, visitor: IExpressionVisitor) -> Any:
        return visitor.visit_operator(self)


@dataclass
class UnaryOperator(IOperator):
    """Unary operator expression."""
    operator: str
    operand: IExpression

    def accept(self, visitor: IExpressionVisitor) -> Any:
        return visitor.visit_operator(self)


class ExpressionBuilder:
    """Builder for SQL expressions."""

    @staticmethod
    def column(table: str, name: str, alias: Optional[str] = None) -> Column:
        return Column(table=table, name=name, alias=alias)

    @staticmethod
    def literal(value: Any, type_: Optional[type] = None) -> Literal:
        if type_ is None:
            type_ = type(value)
        return Literal(value=value, type_=type_)

    @staticmethod
    def function(name: str, *args: IExpression, distinct: bool = False) -> Function:
        return Function(name=name, args=list(args), distinct=distinct)

    @staticmethod
    def eq(left: IExpression, right: IExpression) -> BinaryOperator:
        return BinaryOperator(left=left, operator="=", right=right)

    @staticmethod
    def ne(left: IExpression, right: IExpression) -> BinaryOperator:
        return BinaryOperator(left=left, operator="!=", right=right)

    @staticmethod
    def gt(left: IExpression, right: IExpression) -> BinaryOperator:
        return BinaryOperator(left=left, operator=">", right=right)

    @staticmethod
    def lt(left: IExpression, right: IExpression) -> BinaryOperator:
        return BinaryOperator(left=left, operator="<", right=right)

    @staticmethod
    def ge(left: IExpression, right: IExpression) -> BinaryOperator:
        return BinaryOperator(left=left, operator=">=", right=right)

    @staticmethod
    def le(left: IExpression, right: IExpression) -> BinaryOperator:
        return BinaryOperator(left=left, operator="<=", right=right)

    @staticmethod
    def and_(*conditions: IExpression) -> IExpression:
        result = conditions[0]
        for condition in conditions[1:]:
            result = BinaryOperator(left=result, operator="AND", right=condition)
        return result

    @staticmethod
    def or_(*conditions: IExpression) -> IExpression:
        result = conditions[0]
        for condition in conditions[1:]:
            result = BinaryOperator(left=result, operator="OR", right=condition)
        return result

    @staticmethod
    def not_(condition: IExpression) -> UnaryOperator:
        return UnaryOperator(operator="NOT", operand=condition)


class ExpressionEvaluator(IExpressionVisitor):
    """Evaluates expressions against a row of data."""

    def __init__(self, row: Dict[str, Any]):
        self.row = row

    def visit_column(self, column: Column) -> Any:
        key = f"{column.table}.{column.name}" if column.table else column.name
        return self.row.get(key)

    def visit_literal(self, literal: Literal) -> Any:
        return literal.value

    def visit_function(self, function: Function) -> Any:
        # Implementation would handle various SQL functions
        pass

    def visit_operator(self, operator: IOperator) -> Any:
        if isinstance(operator, BinaryOperator):
            left = operator.left.accept(self)
            right = operator.right.accept(self)

            if operator.operator == "=":
                return left == right
            elif operator.operator == "!=":
                return left != right
            elif operator.operator == ">":
                return left > right
            elif operator.operator == "<":
                return left < right
            elif operator.operator == ">=":
                return left >= right
            elif operator.operator == "<=":
                return left <= right
            elif operator.operator == "AND":
                return left and right
            elif operator.operator == "OR":
                return left or right

        elif isinstance(operator, UnaryOperator):
            value = operator.operand.accept(self)

            if operator.operator == "NOT":
                return not value

        raise ValueError(f"Unknown operator: {operator.operator}")
