from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Generic, TypeVar

T = TypeVar('T')


class IExpression(ABC):
    """Base interface for all SQL expressions."""

    @abstractmethod
    def accept(self, visitor: 'IExpressionVisitor') -> Any:
        """Accept a visitor to process this expression."""
        pass


class IExpressionVisitor(ABC):
    """Visitor interface for processing expressions."""

    @abstractmethod
    def visit_column(self, column: 'IColumn') -> Any: pass

    @abstractmethod
    def visit_literal(self, literal: 'ILiteral') -> Any: pass

    @abstractmethod
    def visit_function(self, function: 'IFunction') -> Any: pass

    @abstractmethod
    def visit_operator(self, operator: 'IOperator') -> Any: pass


class IStatement(ABC):
    """Base interface for all SQL statements."""

    @abstractmethod
    def accept(self, visitor: 'IStatementVisitor') -> Any:
        """Accept a visitor to process this statement."""
        pass


class IStatementVisitor(ABC):
    """Visitor interface for processing statements."""

    @abstractmethod
    def visit_select(self, select: 'ISelectStatement') -> Any: pass

    @abstractmethod
    def visit_insert(self, insert: 'IInsertStatement') -> Any: pass

    @abstractmethod
    def visit_update(self, update: 'IUpdateStatement') -> Any: pass

    @abstractmethod
    def visit_delete(self, delete: 'IDeleteStatement') -> Any: pass


class IExecutionPlan(ABC):
    """Interface for query execution plans."""

    @abstractmethod
    def execute(self, context: 'IExecutionContext') -> 'IResultSet':
        """Execute this plan with the given context."""
        pass


class IExecutionContext(ABC):
    """Interface for execution context."""

    @abstractmethod
    def get_storage(self) -> 'IStorage':
        """Get the storage interface."""
        pass

    @abstractmethod
    def get_transaction(self) -> 'ITransaction':
        """Get the current transaction."""
        pass


class IStorage(ABC):
    """Interface for data storage."""

    @abstractmethod
    def read(self, table: str, columns: List[str],
             predicate: Optional['IPredicate'] = None) -> 'IResultSet':
        """Read data from storage."""
        pass

    @abstractmethod
    def write(self, table: str, data: List[Dict[str, Any]]) -> int:
        """Write data to storage."""
        pass

    @abstractmethod
    def update(self, table: str, updates: Dict[str, Any],
               predicate: Optional['IPredicate'] = None) -> int:
        """Update data in storage."""
        pass

    @abstractmethod
    def delete(self, table: str, predicate: Optional['IPredicate'] = None) -> int:
        """Delete data from storage."""
        pass


class IResultSet(ABC, Generic[T]):
    """Interface for query results."""

    @abstractmethod
    def next(self) -> Optional[T]:
        """Get next result."""
        pass

    @abstractmethod
    def all(self) -> List[T]:
        """Get all results."""
        pass


class IOptimizer(ABC):
    """Interface for query optimization."""

    @abstractmethod
    def optimize(self, plan: IExecutionPlan) -> IExecutionPlan:
        """Optimize an execution plan."""
        pass


class IPredicate(ABC):
    """Interface for query predicates."""

    @abstractmethod
    def evaluate(self, row: Dict[str, Any]) -> bool:
        """Evaluate this predicate against a row."""
        pass

    @abstractmethod
    def simplify(self) -> 'IPredicate':
        """Simplify this predicate."""
        pass


class IIndex(ABC):
    """Interface for database indexes."""

    @abstractmethod
    def get(self, key: Any) -> List[int]:
        """Get row IDs for a key."""
        pass

    @abstractmethod
    def put(self, key: Any, row_id: int) -> None:
        """Add a key-rowID mapping."""
        pass

    @abstractmethod
    def remove(self, key: Any, row_id: int) -> None:
        """Remove a key-rowID mapping."""
        pass


class ITransaction(ABC):
    """Interface for database transactions."""

    @abstractmethod
    def begin(self) -> None:
        """Begin transaction."""
        pass

    @abstractmethod
    def commit(self) -> None:
        """Commit transaction."""
        pass

    @abstractmethod
    def rollback(self) -> None:
        """Rollback transaction."""
        pass

    @abstractmethod
    def is_active(self) -> bool:
        """Check if transaction is active."""
        pass
