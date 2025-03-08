"""Query execution engine for JSON database.

This module implements various execution plans for different types of SQL operations.
It provides a flexible execution engine that can handle complex queries while
maintaining efficiency when working with JSON storage.

Example:
    ```python
    # Create and execute a table scan
    plan = TableScanPlan("users", ["name", "age"], User.age > 18)
    result = plan.execute(context)
    
    # Create and execute a join
    join_plan = JoinPlan(
        left=TableScanPlan("users", ["id", "name"]),
        right=TableScanPlan("orders", ["user_id", "amount"]),
        condition=User.id == Order.user_id
    )
    ```
"""

from typing import Any, Dict, List, Optional

from .interfaces import (
    IExecutionPlan, IExecutionContext, IResultSet, IPredicate, IExpression
)


class ExecutionPlan(IExecutionPlan):
    """Base class for all execution plans.
    
    This class serves as the foundation for specific execution plan implementations.
    Each subclass represents a different type of database operation (scan, join, etc.)
    and provides its specific execution logic.
    """

    def execute(self, context: IExecutionContext) -> IResultSet:
        """Execute this plan with the given context.
        
        Args:
            context: Execution context containing storage and transaction info.
            
        Returns:
            IResultSet: Results of executing the plan.
            
        Raises:
            NotImplementedError: This is an abstract method.
        """
        raise NotImplementedError


class TableScanPlan(ExecutionPlan):
    """Full table scan execution plan.
    
    This plan performs a full scan of a table, optionally filtering rows
    based on a predicate and selecting specific columns.
    
    Attributes:
        table: Name of the table to scan.
        columns: List of columns to select.
        predicate: Optional filtering condition.
        
    Example:
        ```python
        plan = TableScanPlan("users", ["name", "email"], User.age > 18)
        results = plan.execute(context)
        ```
    """

    def __init__(
            self,
            table: str,
            columns: List[str],
            predicate: Optional[IPredicate] = None
    ):
        """Initialize a table scan plan.
        
        Args:
            table: Name of the table to scan.
            columns: List of columns to select.
            predicate: Optional filtering condition.
        """
        self.table = table
        self.columns = columns
        self.predicate = predicate

    def execute(self, context: IExecutionContext) -> IResultSet:
        """Execute the table scan.
        
        Args:
            context: Execution context containing storage access.
            
        Returns:
            IResultSet: Filtered and projected rows from the table.
        """
        storage = context.get_storage()
        return storage.read(self.table, self.columns, self.predicate)


class JoinPlan(ExecutionPlan):
    """Join execution plan.
    
    This plan performs a join between two tables or intermediate results.
    Supports different join types (INNER, LEFT, RIGHT, FULL) and conditions.
    """



class AggregatePlan(ExecutionPlan):
    """Aggregation execution plan.
    
    This plan performs aggregation operations (COUNT, SUM, AVG, etc.)
    on grouped or ungrouped data.
    """


class SortPlan(ExecutionPlan):
    """Sort execution plan.
    
    This plan sorts results based on one or more columns in
    specified directions (ASC/DESC).
    """


class ProjectPlan(ExecutionPlan):
    """Projection execution plan.
    
    This plan selects specific columns from its input,
    optionally with computed expressions.
    """


class LimitPlan(ExecutionPlan):
    """Limit execution plan.
    
    This plan limits the number of rows returned and/or
    skips a specified number of initial rows.
    """


class InsertPlan(ExecutionPlan):
    """Insert execution plan.
    
    This plan handles insertion of new rows into a table,
    with support for single and bulk inserts.
    """


class UpdatePlan(ExecutionPlan):
    """Update execution plan.
    
    This plan handles updating existing rows in a table
    based on specified conditions.
    """


class DeletePlan(ExecutionPlan):
    """Delete execution plan.
    
    This plan handles deletion of rows from a table
    based on specified conditions.
    """


class SingleRowResult(IResultSet):
    """Result set containing a single row.
    
    This is a specialized result set implementation for operations
    that return exactly one row (e.g., getting by primary key).
    """
