"""Base classes for SQL statement handling.

This module provides the foundation for handling SQL statements in the JSON database.
It implements the Visitor and Builder patterns for flexible statement processing
and construction.

Example:
    ```python
    # Create a statement visitor
    class StatementValidator(StatementVisitor):
        def visit(self, statement: Statement) -> None:
            for clause in statement.get_clauses():
                if not clause.validate():
                    raise ValueError("Invalid clause")
    
    # Create a statement builder
    class SelectBuilder(StatementBuilder[SelectStatement]):
        def add_where(self, condition: Expression) -> None:
            self._statement.where.add_condition(condition)
    ```
"""

from abc import ABC, abstractmethod
from typing import List, Generic, TypeVar

from ..clause.base import Clause

T = TypeVar('T')


class Statement(ABC):
    """Base class for all SQL statements.
    
    This abstract class defines the interface that all SQL statements must implement.
    It supports the Visitor pattern for flexible statement processing.
    
    Example:
        ```python
        class SelectStatement(Statement):
            def accept(self, visitor: StatementVisitor) -> None:
                visitor.visit(self)
                
            def get_clauses(self) -> List[Clause]:
                return [self.where, self.join, self.order_by]
        ```
    """

    @abstractmethod
    def accept(self, visitor: 'StatementVisitor') -> None:
        """Accept a statement visitor.
        
        Args:
            visitor: The visitor that will process this statement.
        """
        pass

    @abstractmethod
    def get_clauses(self) -> List[Clause]:
        """Get all clauses in this statement.
        
        Returns:
            List[Clause]: List of all clauses in the statement.
        """
        pass


class StatementVisitor(ABC):
    """Base visitor for SQL statements.
    
    This abstract class defines the interface for statement visitors,
    which can process different types of statements in various ways
    (validation, optimization, execution, etc.).
    
    Example:
        ```python
        class StatementOptimizer(StatementVisitor):
            def visit(self, statement: Statement) -> None:
                for clause in statement.get_clauses():
                    self._optimize_clause(clause)
        ```
    """

    @abstractmethod
    def visit(self, statement: Statement) -> None:
        """Visit a statement.
        
        Args:
            statement: The statement to process.
        """
        pass


class StatementBuilder(Generic[T], ABC):
    """Base builder for SQL statements.
    
    This abstract class defines the interface for statement builders,
    which construct statements in a step-by-step manner. The type
    parameter T specifies the type of statement being built.
    
    Example:
        ```python
        class SelectBuilder(StatementBuilder[SelectStatement]):
            def add_where(self, condition: Expression) -> None:
                self._statement.where.add_condition(condition)
                
            def add_join(self, table: Table, condition: Expression) -> None:
                self._statement.joins.append(JoinClause(table, condition))
        ```
    """

    @abstractmethod
    def reset(self) -> None:
        """Reset the builder to initial state.
        
        Clears all built components and prepares for a new build.
        """
        pass

    @abstractmethod
    def get_result(self) -> T:
        """Get the built statement.
        
        Returns:
            T: The constructed statement.
        """
        pass


class StatementDirector(ABC):
    """Base director for statement construction.
    
    This abstract class defines the interface for statement directors,
    which coordinate the construction of complex statements using builders.
    It implements the Director role in the Builder pattern.
    
    Example:
        ```python
        class QueryDirector(StatementDirector):
            def construct(self, builder: StatementBuilder) -> None:
                builder.reset()
                builder.add_where(self._build_conditions())
                builder.add_join(self._build_joins())
                builder.add_order_by(self._build_ordering())
        ```
    """

    @abstractmethod
    def construct(self, builder: StatementBuilder) -> None:
        """Construct a statement using the builder.
        
        Args:
            builder: The builder to use for statement construction.
        """
        pass
