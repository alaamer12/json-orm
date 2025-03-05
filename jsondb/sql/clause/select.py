"""SELECT clause implementation for SQL statements.

This module provides the implementation of SELECT clauses for SQL statements
in the JSON database. It supports column selection, DISTINCT operations,
and follows the Builder pattern for clause construction.

Example:
    ```python
    # Create a SELECT clause
    builder = SelectClauseBuilder()
    select = (builder
             .add_column(User.name)
             .add_column(User.email)
             .set_distinct(True)
             .get_result())
             
    # Process the clause
    handler = SelectClauseHandler()
    handler.handle(select)
    ```
"""

from typing import List

from .base import Clause, ClauseVisitor, ClauseBuilder, ClauseHandler
from ..expression import Expression


class SelectClause(Clause):
    """SELECT clause in a SELECT statement.
    
    This class represents the SELECT part of a SQL SELECT statement,
    supporting column selection and DISTINCT operations.
    
    Attributes:
        _columns: List of columns or expressions to select.
        _distinct: Whether to select distinct values only.
        
    Example:
        ```python
        select = SelectClause()
        select.add_column(User.name)
        select.add_column(func.count(Order.id))
        select.set_distinct(True)
        ```
    """

    def __init__(self):
        """Initialize an empty SELECT clause."""
        self._columns: List[Expression] = []
        self._distinct: bool = False

    def add_column(self, column: Expression) -> None:
        """Add a column or expression to select.
        
        Args:
            column: Column or expression to add to the SELECT list.
        """
        self._columns.append(column)

    def set_distinct(self, distinct: bool) -> None:
        """Set whether to select distinct values.
        
        Args:
            distinct: If True, duplicate rows will be removed.
        """
        self._distinct = distinct

    def accept(self, visitor: ClauseVisitor) -> None:
        """Accept a clause visitor.
        
        Args:
            visitor: Visitor to process this clause.
        """
        visitor.visit(self)

    def validate(self) -> bool:
        """Validate the SELECT clause.
        
        Returns:
            bool: True if at least one column is selected.
        """
        return len(self._columns) > 0

    def clone(self) -> 'SelectClause':
        """Create a deep copy of this clause.
        
        Returns:
            SelectClause: A new instance with the same columns and settings.
        """
        clone = SelectClause()
        clone._columns = [col.clone() for col in self._columns]
        clone._distinct = self._distinct
        return clone


class SelectClauseBuilder(ClauseBuilder['SelectClause']):
    """Builder for SELECT clauses.
    
    This class implements the Builder pattern for constructing SELECT
    clauses in a fluent interface style.
    
    Example:
        ```python
        select = (SelectClauseBuilder()
                 .add_column(User.name)
                 .add_column(User.email)
                 .set_distinct(True)
                 .get_result())
        ```
    """

    def __init__(self):
        """Initialize the builder."""
        self.reset()

    def reset(self) -> None:
        """Reset the builder to initial state."""
        self._clause = SelectClause()

    def add_column(self, column: Expression) -> 'SelectClauseBuilder':
        """Add a column to the SELECT clause.
        
        Args:
            column: Column or expression to select.
            
        Returns:
            SelectClauseBuilder: self for method chaining.
        """
        self._clause.add_column(column)
        return self

    def set_distinct(self, distinct: bool) -> 'SelectClauseBuilder':
        """Set whether to select distinct values.
        
        Args:
            distinct: If True, duplicate rows will be removed.
            
        Returns:
            SelectClauseBuilder: self for method chaining.
        """
        self._clause.set_distinct(distinct)
        return self

    def get_result(self) -> SelectClause:
        """Get the built SELECT clause.
        
        Returns:
            SelectClause: The constructed clause.
        """
        clause = self._clause
        self.reset()
        return clause


class SelectClauseHandler(ClauseHandler):
    """Handler for SELECT clauses.
    
    This class implements the Chain of Responsibility pattern for
    processing SELECT clauses, handling tasks like validation,
    optimization, and execution.
    
    Example:
        ```python
        handler = SelectClauseHandler()
        handler.set_next(OptimizationHandler())
        handler.handle(select_clause)
        ```
    """

    def handle(self, clause: Clause) -> None:
        """Handle a clause.
        
        Args:
            clause: Clause to process. If it's a SelectClause,
                   process it before passing to next handler.
        """
        if isinstance(clause, SelectClause):
            # Handle SELECT clause
            self._process_select(clause)
        self._handle_next(clause)

    def _process_select(self, clause: SelectClause) -> None:
        """Process a SELECT clause.
        
        Args:
            clause: SELECT clause to process.
        """
        # Implementation of SELECT clause processing
        pass
