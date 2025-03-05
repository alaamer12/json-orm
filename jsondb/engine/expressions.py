"""Expression system for the JSON database engine.

This module provides the core expression classes used by the query engine
to represent and evaluate SQL expressions. It implements the Visitor pattern
for flexible processing of different expression types.

Example:
    ```python
    # Create expressions
    name_col = Column("name", "users")
    age_col = Column("age", "users")
    age_check = BinaryOperator(age_col, ">", Literal(18))
    
    # Evaluate expressions
    evaluator = ExpressionEvaluator()
    result = age_check.accept(evaluator)
    ```
"""

from dataclasses import dataclass

from .interfaces import (
    IExpressionVisitor,
    IColumn, ILiteral, IOperator
)


@dataclass
class Column(IColumn):
    """Column reference expression.
    
    Represents a reference to a database column in an expression.
    
    Attributes:
        name: Name of the column.
        table: Optional name of the table containing the column.
        alias: Optional alias for the column in query results.
        
    Example:
        ```python
        name_col = Column("name", "users", "user_name")
        ```
    """


@dataclass
class Literal(ILiteral):
    """Literal value expression.
    
    Represents a constant value in an expression.
    
    Attributes:
        value: The literal value.
        type_: Optional type hint for the value.
        
    Example:
        ```python
        age_limit = Literal(18, int)
        name_pattern = Literal("%John%", str)
        ```
    """


@dataclass
class BinaryOperator(IOperator):
    """Binary operator expression.
    
    Represents an operation between two expressions.
    
    Attributes:
        left: Left operand expression.
        operator: Operator symbol (e.g., '=', '>', '+').
        right: Right operand expression.
        
    Example:
        ```python
        age_check = BinaryOperator(
            Column("age", "users"),
            ">",
            Literal(18)
        )
        ```
    """


@dataclass
class UnaryOperator(IOperator):
    """Unary operator expression.
    
    Represents an operation on a single expression.
    
    Attributes:
        operator: Operator symbol (e.g., 'NOT', '-').
        operand: The expression to operate on.
        
    Example:
        ```python
        not_active = UnaryOperator(
            "NOT",
            Column("is_active", "users")
        )
        ```
    """


class ExpressionBuilder:
    """Builder for SQL expressions.
    
    Provides a fluent interface for constructing complex SQL expressions.
    
    Example:
        ```python
        builder = ExpressionBuilder()
        expr = (builder
               .column("age", "users")
               .gt(18)
               .and_()
               .column("status")
               .eq("active")
               .build())
        ```
    """


class ExpressionEvaluator(IExpressionVisitor):
    """Evaluates expressions against a row of data.
    
    Implements the visitor pattern to evaluate different types of
    expressions against actual data values.
    
    Example:
        ```python
        evaluator = ExpressionEvaluator()
        row = {"age": 25, "name": "John"}
        result = expression.accept(evaluator.with_row(row))
        ```
    """