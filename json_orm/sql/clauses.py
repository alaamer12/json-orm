"""SQL clause definitions for the JSON database.

This module defines the various SQL clauses that can appear in SQL statements,
such as WHERE, JOIN, ORDER BY, etc. Each clause is implemented as a dataclass
for efficient storage and manipulation of clause data.

Example:
    ```python
    # Create a WHERE clause
    where = WhereClause()
    where.add_condition(User.age > 18)
    
    # Create a JOIN clause
    join = JoinClause(
        table=Order,
        condition=User.id == Order.user_id,
        join_type="LEFT"
    )
    
    # Create an ORDER BY clause
    order = OrderByClause()
    order.clauses = [User.name]
    order.directions = ["ASC"]
    ```
"""

from dataclasses import dataclass, field
from typing import List, Optional, Union

from .expressions import Expression, Column, Table


@dataclass
class WhereClause:
    """Represents a WHERE clause in a SQL statement.
    
    This class handles the filtering conditions in SQL queries.
    Multiple conditions can be added and are combined with AND logic.
    
    Attributes:
        conditions: List of expressions that form the WHERE conditions.
        
    Example:
        ```python
        where = WhereClause()
        where.add_condition(User.age > 18)
        where.add_condition(User.status == "active")
        ```
    """
    conditions: List[Expression] = field(default_factory=list)

    def add_condition(self, condition: Expression) -> None:
        """Add a condition to the WHERE clause.
        
        Args:
            condition: Expression representing the condition to add.
        """
        self.conditions.append(condition)


@dataclass
class JoinClause:
    """Represents a JOIN clause in a SQL statement.
    
    This class handles table joins with specified conditions and join types.
    Supports INNER, LEFT, RIGHT, and FULL joins.
    
    Attributes:
        table: The table to join with.
        condition: Expression specifying the join condition.
        join_type: Type of join (INNER, LEFT, RIGHT, FULL).
        
    Example:
        ```python
        join = JoinClause(
            table=Order,
            condition=User.id == Order.user_id,
            join_type="LEFT"
        )
        ```
    """
    table: Table
    condition: Expression
    join_type: str = "INNER"  # INNER, LEFT, RIGHT, FULL


@dataclass
class OrderByClause:
    """Represents an ORDER BY clause in a SQL statement.
    
    This class handles result ordering by specified columns or expressions.
    Each column can have its own sort direction.
    
    Attributes:
        clauses: List of columns or expressions to order by.
        directions: List of sort directions ("ASC" or "DESC").
        
    Example:
        ```python
        order = OrderByClause()
        order.clauses = [User.name, User.age]
        order.directions = ["ASC", "DESC"]
        ```
    """
    clauses: List[Union[Column, Expression]] = field(default_factory=list)
    directions: List[str] = field(default_factory=list)  # ASC or DESC


@dataclass
class GroupByClause:
    """Represents a GROUP BY clause in a SQL statement.
    
    This class handles result grouping by specified columns.
    Often used with aggregate functions.
    
    Attributes:
        columns: List of columns to group by.
        
    Example:
        ```python
        group = GroupByClause()
        group.columns = [User.country, User.city]
        ```
    """
    columns: List[Column] = field(default_factory=list)


@dataclass
class HavingClause:
    """Represents a HAVING clause in a SQL statement.
    
    This class handles filtering conditions for grouped results.
    Used in conjunction with GROUP BY clauses.
    
    Attributes:
        condition: Expression specifying the having condition.
        
    Example:
        ```python
        having = HavingClause(
            condition=func.count(Order.id) > 5
        )
        ```
    """
    condition: Expression


@dataclass
class LimitClause:
    """Represents a LIMIT clause in a SQL statement.
    
    This class handles result limiting and pagination.
    Supports both limit and offset for paginated results.
    
    Attributes:
        count: Maximum number of rows to return.
        offset: Number of rows to skip (for pagination).
        
    Example:
        ```python
        # Get 10 rows starting from position 20
        limit = LimitClause(count=10, offset=20)
        ```
    """
    count: int
    offset: Optional[int] = None


@dataclass
class SetClause:
    """Represents a SET clause in an UPDATE statement.
    
    This class handles column value assignments in UPDATE statements.
    Each assignment pairs a column with its new value expression.
    
    Attributes:
        assignments: List of (column, value) pairs for updating.
        
    Example:
        ```python
        set_clause = SetClause()
        set_clause.assignments = [
            (User.status, "inactive"),
            (User.updated_at, func.now())
        ]
        ```
    """
    assignments: List[tuple[Column, Expression]] = field(default_factory=list)


@dataclass
class ValuesClause:
    """Represents a VALUES clause in an INSERT statement.
    
    This class handles value specifications for INSERT statements.
    Supports inserting multiple rows with specified column values.
    
    Attributes:
        columns: List of columns to insert into.
        values: List of value lists, one per row to insert.
        
    Example:
        ```python
        values = ValuesClause(
            columns=[User.name, User.email],
            values=[
                ["John Doe", "john@example.com"],
                ["Jane Doe", "jane@example.com"]
            ]
        )
        ```
    """
    columns: List[Column]
    values: List[List[Expression]]
