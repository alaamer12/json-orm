"""Query planning system for JSON database.

This module is responsible for creating efficient execution plans for SQL queries.
It analyzes queries and determines the best strategy for execution, considering
factors like:
- Available indexes
- Table sizes
- Join conditions
- Filter selectivity

Example:
    ```python
    # Create a query planner
    planner = QueryPlanner()
    
    # Plan a query
    select_stmt = select(User).where(User.age > 18).join(Order)
    plan = select_stmt.accept(planner)
    
    # Execute the plan
    result = plan.execute(context)
    ```
"""

from .interfaces import (
    IStatementVisitor
)


class QueryPlanner(IStatementVisitor):
    """Plans query execution strategies.
    
    This class analyzes SQL statements and creates optimal execution plans.
    It implements the visitor pattern to handle different types of statements
    and considers various optimization opportunities.
    
    Attributes:
        optimizer: Query optimizer for improving plans
        stats: Statistics about tables and columns
        
    Example:
        ```python
        planner = QueryPlanner()
        
        # Plan a simple query
        plan = planner.visit_select(
            select(User)
            .where(User.age > 18)
            .order_by(User.name)
        )
        
        # Plan a complex join
        plan = planner.visit_select(
            select(User, Order)
            .join(Order)
            .where(User.status == 'active')
            .group_by(User.country)
            .having(func.count(Order.id) > 5)
        )
        ```
    """