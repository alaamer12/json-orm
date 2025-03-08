"""Core interfaces for the JSON database engine.

This module defines the abstract base classes that form the foundation of the database engine.
It follows the Visitor pattern for processing expressions and statements, and provides
interfaces for storage, optimization, and transaction management.

Example:
    ```python
    class MyStorage(IStorage):
        def read(self, table: str, columns: List[str],
                predicate: Optional[IPredicate] = None) -> IResultSet:
            # Implementation
            pass
    ```

Typical usage example:
    ```python
    storage = MyStorage()
    context = ExecutionContext(storage)
    plan = QueryPlanner().create_plan(query)
    result = plan.execute(context)
    ```
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Generic, TypeVar

T = TypeVar('T')


class IExpression(ABC):
    """Abstract base class for all SQL expressions.

    This class defines the interface that all SQL expressions must implement.
    It follows the Visitor pattern to allow for flexible processing of expressions.

    Attributes:
        None

    Example:
        ```python
        class Column(IExpression):
            def accept(self, visitor: IExpressionVisitor) -> Any:
                return visitor.visit_column(self)
        ```
    """

    @abstractmethod
    def accept(self, visitor: 'IExpressionVisitor') -> Any:
        """Accepts a visitor to process this expression.

        Args:
            visitor: The visitor that will process this expression.

        Returns:
            Any: The result of the visitor's processing.
        """
        pass


class IExpressionVisitor(ABC):
    """Visitor interface for processing SQL expressions.

    This interface defines the methods that must be implemented to process
    different types of SQL expressions using the Visitor pattern.

    Example:
        ```python
        class ExpressionPrinter(IExpressionVisitor):
            def visit_column(self, column: IColumn) -> str:
                return column.name
        ```
    """

    @abstractmethod
    def visit_column(self, column: 'IColumn') -> Any:
        """Process a column expression.

        Args:
            column: The column expression to process.

        Returns:
            Any: The result of processing the column.
        """
        pass

    @abstractmethod
    def visit_literal(self, literal: 'ILiteral') -> Any:
        """Process a literal expression.

        Args:
            literal: The literal expression to process.

        Returns:
            Any: The result of processing the literal.
        """
        pass

    @abstractmethod
    def visit_function(self, function: 'IFunction') -> Any:
        """Process a function expression.

        Args:
            function: The function expression to process.

        Returns:
            Any: The result of processing the function.
        """
        pass

    @abstractmethod
    def visit_operator(self, operator: 'IOperator') -> Any:
        """Process an operator expression.

        Args:
            operator: The operator expression to process.

        Returns:
            Any: The result of processing the operator.
        """
        pass


class IStatement(ABC):
    """Abstract base class for all SQL statements.

    This class defines the interface that all SQL statements must implement.
    It follows the Visitor pattern to allow for flexible processing of statements.

    Example:
        ```python
        class SelectStatement(IStatement):
            def accept(self, visitor: IStatementVisitor) -> Any:
                return visitor.visit_select(self)
        ```
    """

    @abstractmethod
    def accept(self, visitor: 'IStatementVisitor') -> Any:
        """Accepts a visitor to process this statement.

        Args:
            visitor: The visitor that will process this statement.

        Returns:
            Any: The result of the visitor's processing.
        """
        pass


class IStatementVisitor(ABC):
    """Visitor interface for processing SQL statements.

    This interface defines the methods that must be implemented to process
    different types of SQL statements using the Visitor pattern.

    Example:
        ```python
        class StatementExecutor(IStatementVisitor):
            def visit_select(self, select: ISelectStatement) -> IResultSet:
                # Execute SELECT statement
                pass
        ```
    """

    @abstractmethod
    def visit_select(self, select: 'ISelectStatement') -> Any:
        """Process a SELECT statement.

        Args:
            select: The SELECT statement to process.

        Returns:
            Any: The result of processing the SELECT statement.
        """
        pass

    @abstractmethod
    def visit_insert(self, insert: 'IInsertStatement') -> Any:
        """Process an INSERT statement.

        Args:
            insert: The INSERT statement to process.

        Returns:
            Any: The result of processing the INSERT statement.
        """
        pass

    @abstractmethod
    def visit_update(self, update: 'IUpdateStatement') -> Any:
        """Process an UPDATE statement.

        Args:
            update: The UPDATE statement to process.

        Returns:
            Any: The result of processing the UPDATE statement.
        """
        pass

    @abstractmethod
    def visit_delete(self, delete: 'IDeleteStatement') -> Any:
        """Process a DELETE statement.

        Args:
            delete: The DELETE statement to process.

        Returns:
            Any: The result of processing the DELETE statement.
        """
        pass


class IExecutionPlan(ABC):
    """Interface for query execution plans.

    This class defines the interface for executing query plans, which represent
    the optimized sequence of operations needed to execute a query.

    Example:
        ```python
        class TableScanPlan(IExecutionPlan):
            def execute(self, context: IExecutionContext) -> IResultSet:
                # Perform table scan
                pass
        ```
    """

    @abstractmethod
    def execute(self, context: 'IExecutionContext') -> 'IResultSet':
        """Execute this plan with the given context.

        Args:
            context: The execution context containing storage and transaction info.

        Returns:
            IResultSet: The results of executing the plan.
        """
        pass


class IExecutionContext(ABC):
    """Interface for query execution context.

    This class defines the interface for the execution context, which provides
    access to storage and transaction information during query execution.

    Example:
        ```python
        class ExecutionContext(IExecutionContext):
            def __init__(self, storage: IStorage):
                self._storage = storage
                self._transaction = Transaction()
        ```
    """

    @abstractmethod
    def get_storage(self) -> 'IStorage':
        """Get the storage interface.

        Returns:
            IStorage: The storage interface for data access.
        """
        pass

    @abstractmethod
    def get_transaction(self) -> 'ITransaction':
        """Get the current transaction.

        Returns:
            ITransaction: The current active transaction.
        """
        pass


class IStorage(ABC):
    """Interface for data storage operations.

    This class defines the interface for storage operations, providing methods
    for reading, writing, updating, and deleting data.

    Example:
        ```python
        class JsonStorage(IStorage):
            def read(self, table: str, columns: List[str],
                    predicate: Optional[IPredicate] = None) -> IResultSet:
                # Read from JSON files
                pass
        ```
    """

    @abstractmethod
    def read(self, table: str, columns: List[str],
             predicate: Optional['IPredicate'] = None) -> 'IResultSet':
        """Read data from storage.

        Args:
            table: Name of the table to read from.
            columns: List of column names to read.
            predicate: Optional predicate to filter rows.

        Returns:
            IResultSet: The query results.
        """
        pass

    @abstractmethod
    def write(self, table: str, data: List[Dict[str, Any]]) -> int:
        """Write data to storage.

        Args:
            table: Name of the table to write to.
            data: List of rows to write.

        Returns:
            int: Number of rows written.
        """
        pass

    @abstractmethod
    def update(self, table: str, updates: Dict[str, Any],
               predicate: Optional['IPredicate'] = None) -> int:
        """Update data in storage.

        Args:
            table: Name of the table to update.
            updates: Dictionary of column-value pairs to update.
            predicate: Optional predicate to filter rows.

        Returns:
            int: Number of rows updated.
        """
        pass

    @abstractmethod
    def delete(self, table: str, predicate: Optional['IPredicate'] = None) -> int:
        """Delete data from storage.

        Args:
            table: Name of the table to delete from.
            predicate: Optional predicate to filter rows.

        Returns:
            int: Number of rows deleted.
        """
        pass


class IResultSet(ABC, Generic[T]):
    """Interface for query results.

    This class defines the interface for accessing query results, supporting
    both iterator-style access and bulk retrieval.

    Example:
        ```python
        class JsonResultSet(IResultSet[Dict[str, Any]]):
            def next(self) -> Optional[Dict[str, Any]]:
                # Return next row from JSON data
                pass
        ```
    """

    @abstractmethod
    def next(self) -> Optional[T]:
        """Get the next result.

        Returns:
            Optional[T]: The next result, or None if no more results.
        """
        pass

    @abstractmethod
    def all(self) -> List[T]:
        """Get all remaining results.

        Returns:
            List[T]: List of all remaining results.
        """
        pass


class IOptimizer(ABC):
    """Interface for query optimization.

    This class defines the interface for query optimization, which transforms
    execution plans to improve performance.

    Example:
        ```python
        class SimpleOptimizer(IOptimizer):
            def optimize(self, plan: IExecutionPlan) -> IExecutionPlan:
                # Apply optimization rules
                pass
        ```
    """

    @abstractmethod
    def optimize(self, plan: IExecutionPlan) -> IExecutionPlan:
        """Optimize an execution plan.

        Args:
            plan: The execution plan to optimize.

        Returns:
            IExecutionPlan: The optimized execution plan.
        """
        pass


class IPredicate(ABC):
    """Interface for query predicates.

    This class defines the interface for query predicates, which are used
    to filter rows during query execution.

    Example:
        ```python
        class ComparisonPredicate(IPredicate):
            def evaluate(self, row: Dict[str, Any]) -> bool:
                # Evaluate comparison
                pass
        ```
    """

    @abstractmethod
    def evaluate(self, row: Dict[str, Any]) -> bool:
        """Evaluate this predicate against a row.

        Args:
            row: The row to evaluate against.

        Returns:
            bool: True if the row matches the predicate, False otherwise.
        """
        pass

    @abstractmethod
    def simplify(self) -> 'IPredicate':
        """Simplify this predicate.

        Returns:
            IPredicate: A simplified version of this predicate.
        """
        pass


class IIndex(ABC):
    """Interface for database indexes.

    This class defines the interface for database indexes, which provide
    efficient access to rows based on column values.

    Example:
        ```python
        class HashIndex(IIndex):
            def get(self, key: Any) -> List[int]:
                # Look up row IDs in hash table
                pass
        ```
    """

    @abstractmethod
    def get(self, key: Any) -> List[int]:
        """Get row IDs for a key.

        Args:
            key: The key to look up.

        Returns:
            List[int]: List of row IDs matching the key.
        """
        pass

    @abstractmethod
    def put(self, key: Any, row_id: int) -> None:
        """Add a key-rowID mapping.

        Args:
            key: The key to map.
            row_id: The row ID to map to.
        """
        pass

    @abstractmethod
    def remove(self, key: Any, row_id: int) -> None:
        """Remove a key-rowID mapping.

        Args:
            key: The key to remove.
            row_id: The row ID to remove.
        """
        pass


class ITransaction(ABC):
    """Interface for database transactions.

    This class defines the interface for database transactions, providing
    ACID properties for database operations.

    Example:
        ```python
        class Transaction(ITransaction):
            def begin(self) -> None:
                self._active = True
                self._savepoint = self._create_savepoint()
        ```
    """

    @abstractmethod
    def begin(self) -> None:
        """Begin a new transaction."""
        pass

    @abstractmethod
    def commit(self) -> None:
        """Commit the current transaction."""
        pass

    @abstractmethod
    def rollback(self) -> None:
        """Rollback the current transaction."""
        pass

    @abstractmethod
    def is_active(self) -> bool:
        """Check if a transaction is currently active.

        Returns:
            bool: True if a transaction is active, False otherwise.
        """
        pass
