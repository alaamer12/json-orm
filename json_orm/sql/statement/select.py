"""SELECT statement implementation for the JSON database.

This module provides classes for representing and building SELECT statements.
It implements a complete SQL SELECT statement with support for all standard
clauses including WHERE, JOIN, GROUP BY, etc.

Example:
    ```python
    # Create a SELECT statement
    stmt = SelectStatement()
    stmt.select = SelectClause([User.name, User.email])
    stmt.where = WhereClause(User.age > 18)
    stmt.order_by = OrderByClause([User.name], ["ASC"])
    
    # Build a SELECT statement
    builder = SelectStatementBuilder()
    director = SelectStatementDirector()
    director.construct(builder)
    stmt = builder.get_result()
    ```
"""

from typing import List, Optional

from .base import Statement, StatementBuilder, StatementDirector
from ..clause.groupby import GroupByClause
from ..clause.having import HavingClause
from ..clause.join import JoinClause
from ..clause.limit import LimitClause
from ..clause.orderby import OrderByClause
from ..clause.select import SelectClause
from ..clause.where import WhereClause


class SelectStatement(Statement):
    """Represents a SELECT statement.
    
    This class implements a complete SQL SELECT statement with support
    for all standard clauses. It follows the composite pattern, containing
    multiple clause objects that form the complete statement.
    
    Attributes:
        _select: The SELECT clause specifying columns to retrieve.
        _where: Optional WHERE clause for filtering.
        _joins: List of JOIN clauses for table joining.
        _group_by: Optional GROUP BY clause for grouping.
        _having: Optional HAVING clause for group filtering.
        _order_by: Optional ORDER BY clause for sorting.
        _limit: Optional LIMIT clause for result limiting.
        
    Example:
        ```python
        stmt = SelectStatement()
        stmt.select = SelectClause([User.name, User.email])
        stmt.where = WhereClause(User.age > 18)
        stmt.joins.append(
            JoinClause(Order, User.id == Order.user_id)
        )
        stmt.order_by = OrderByClause([User.name], ["ASC"])
        ```
    """

    def __init__(self):
        """Initialize an empty SELECT statement."""
        self._select: Optional[SelectClause] = None
        self._where: Optional[WhereClause] = None
        self._joins: List[JoinClause] = []
        self._group_by: Optional[GroupByClause] = None
        self._having: Optional[HavingClause] = None
        self._order_by: Optional[OrderByClause] = None
        self._limit: Optional[LimitClause] = None


class SelectStatementBuilder(StatementBuilder['SelectStatement']):
    """Builder for SELECT statements.
    
    This class implements the Builder pattern for constructing SELECT
    statements. It provides methods for adding each type of clause
    and ensures proper statement construction.
    
    Example:
        ```python
        builder = SelectStatementBuilder()
        builder.add_select([User.name, User.email])
        builder.add_where(User.age > 18)
        builder.add_order_by([User.name], ["ASC"])
        stmt = builder.get_result()
        ```
    """


class SelectStatementDirector(StatementDirector):
    """Director for SELECT statement construction.
    
    This class implements the Director role in the Builder pattern
    for SELECT statements. It coordinates the construction of complex
    SELECT statements with multiple clauses.
    
    Example:
        ```python
        # Create a director for user analytics queries
        class UserAnalyticsDirector(SelectStatementDirector):
            def construct(self, builder: SelectStatementBuilder) -> None:
                builder.add_select([
                    User.country,
                    func.count(User.id).as_("user_count")
                ])
                builder.add_where(User.status == "active")
                builder.add_group_by([User.country])
                builder.add_having(func.count(User.id) > 100)
        ```
    """
