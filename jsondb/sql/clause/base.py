from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic

T = TypeVar('T')


class Clause(ABC):
    """Base class for all SQL clauses."""

    @abstractmethod
    def accept(self, visitor: 'ClauseVisitor') -> None:
        """Accept a clause visitor."""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Validate clause structure."""
        pass

    @abstractmethod
    def clone(self) -> 'Clause':
        """Create a deep copy of this clause."""
        pass


class ClauseVisitor(ABC):
    """Base visitor for SQL clauses."""

    @abstractmethod
    def visit(self, clause: Clause) -> None:
        """Visit a clause."""
        pass


class ClauseBuilder(Generic[T], ABC):
    """Base builder for SQL clauses."""

    @abstractmethod
    def reset(self) -> None:
        """Reset the builder to initial state."""
        pass

    @abstractmethod
    def get_result(self) -> T:
        """Get the built clause."""
        pass


class ClauseComposite(Clause):
    """Base class for composite clauses."""

    def __init__(self):
        self._children: List[Clause] = []

    def add(self, clause: Clause) -> None:
        """Add a child clause."""
        self._children.append(clause)

    def remove(self, clause: Clause) -> None:
        """Remove a child clause."""
        self._children.remove(clause)

    def get_children(self) -> List[Clause]:
        """Get all child clauses."""
        return self._children.copy()

    def validate(self) -> bool:
        """Validate all child clauses."""
        return all(child.validate() for child in self._children)

    def clone(self) -> 'ClauseComposite':
        """Create a deep copy."""
        clone = type(self)()
        for child in self._children:
            clone.add(child.clone())
        return clone


class ClauseHandler(ABC):
    """Base handler for clause processing."""

    def __init__(self):
        self._next_handler: Optional['ClauseHandler'] = None

    def set_next(self, handler: 'ClauseHandler') -> 'ClauseHandler':
        """Set the next handler in the chain."""
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, clause: Clause) -> None:
        """Handle a clause."""
        pass

    def _handle_next(self, clause: Clause) -> None:
        """Pass clause to next handler if exists."""
        if self._next_handler:
            self._next_handler.handle(clause)
