from abc import ABC, abstractmethod
from typing import List, Generic, TypeVar

from ..clause.base import Clause

T = TypeVar('T')


class Statement(ABC):
    """Base class for all SQL statements."""

    @abstractmethod
    def accept(self, visitor: 'StatementVisitor') -> None:
        """Accept a statement visitor."""
        pass

    @abstractmethod
    def get_clauses(self) -> List[Clause]:
        """Get all clauses in this statement."""
        pass


class StatementVisitor(ABC):
    """Base visitor for SQL statements."""

    @abstractmethod
    def visit(self, statement: Statement) -> None:
        """Visit a statement."""
        pass


class StatementBuilder(Generic[T], ABC):
    """Base builder for SQL statements."""

    @abstractmethod
    def reset(self) -> None:
        """Reset the builder to initial state."""
        pass

    @abstractmethod
    def get_result(self) -> T:
        """Get the built statement."""
        pass


class StatementDirector(ABC):
    """Base director for statement construction."""

    @abstractmethod
    def construct(self, builder: StatementBuilder) -> None:
        """Construct a statement using the builder."""
        pass
