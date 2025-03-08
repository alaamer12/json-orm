"""Base classes for SQL clause handling.

This module provides the foundation for handling SQL clauses in the JSON database.
It implements the Composite, Visitor, and Chain of Responsibility patterns to
create a flexible and extensible clause processing system.

Example:
    ```python
    # Create a composite WHERE clause
    where = WhereClause()
    where.add(ComparisonClause(User.age, ">", 18))
    where.add(ComparisonClause(User.status, "=", "active"))
    
    # Process the clause
    validator = ClauseValidator()
    optimizer = ClauseOptimizer()
    validator.set_next(optimizer)
    validator.handle(where)
    ```
"""

from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic

T = TypeVar('T')


class Clause(ABC):
    """Base class for all SQL clauses.
    
    This abstract class defines the interface that all SQL clauses must implement.
    It supports the Visitor pattern for flexible clause processing.
    
    Example:
        ```python
        class WhereClause(Clause):
            def accept(self, visitor: ClauseVisitor) -> None:
                visitor.visit(self)
                
            def validate(self) -> bool:
                return self.condition is not None
        ```
    """

    @abstractmethod
    def accept(self, visitor: 'ClauseVisitor') -> None:
        """Accept a clause visitor.
        
        Args:
            visitor: The visitor that will process this clause.
        """
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Validate clause structure.
        
        Returns:
            bool: True if the clause is valid, False otherwise.
        """
        pass

    @abstractmethod
    def clone(self) -> 'Clause':
        """Create a deep copy of this clause.
        
        Returns:
            Clause: A new instance with the same structure and values.
        """
        pass


class ClauseVisitor(ABC):
    """Base visitor for SQL clauses.
    
    This abstract class defines the interface for clause visitors, which
    can process different types of clauses in various ways (validation,
    optimization, execution, etc.).
    
    Example:
        ```python
        class ClauseValidator(ClauseVisitor):
            def visit(self, clause: Clause) -> None:
                if not clause.validate():
                    raise ValueError("Invalid clause")
        ```
    """

    @abstractmethod
    def visit(self, clause: Clause) -> None:
        """Visit a clause.
        
        Args:
            clause: The clause to process.
        """
        pass


class ClauseBuilder(Generic[T], ABC):
    """Base builder for SQL clauses.
    
    This abstract class defines the interface for clause builders, which
    construct clauses in a step-by-step manner.
    
    Example:
        ```python
        class WhereBuilder(ClauseBuilder[WhereClause]):
            def add_condition(self, column: str, op: str, value: Any) -> None:
                self._conditions.append((column, op, value))
                
            def get_result(self) -> WhereClause:
                return WhereClause(self._conditions)
        ```
    """

    @abstractmethod
    def reset(self) -> None:
        """Reset the builder to initial state."""
        pass

    @abstractmethod
    def get_result(self) -> T:
        """Get the built clause.
        
        Returns:
            T: The constructed clause.
        """
        pass


class ClauseComposite(Clause):
    """Base class for composite clauses.
    
    This class implements the Composite pattern for SQL clauses,
    allowing clauses to be nested within other clauses.
    
    Example:
        ```python
        # Create a composite WHERE clause
        where = WhereClause()
        where.add(ComparisonClause(User.age, ">", 18))
        where.add(ComparisonClause(User.status, "=", "active"))
        ```
    """

    def __init__(self):
        """Initialize an empty composite clause."""
        self._children: List[Clause] = []

    def add(self, clause: Clause) -> None:
        """Add a child clause.
        
        Args:
            clause: The clause to add as a child.
        """
        self._children.append(clause)

    def remove(self, clause: Clause) -> None:
        """Remove a child clause.
        
        Args:
            clause: The clause to remove.
        """
        self._children.remove(clause)

    def get_children(self) -> List[Clause]:
        """Get all child clauses.
        
        Returns:
            List[Clause]: A copy of the list of child clauses.
        """
        return self._children.copy()

    def validate(self) -> bool:
        """Validate all child clauses.
        
        Returns:
            bool: True if all children are valid, False otherwise.
        """
        return all(child.validate() for child in self._children)

    def clone(self) -> 'ClauseComposite':
        """Create a deep copy.
        
        Returns:
            ClauseComposite: A new instance with cloned children.
        """
        clone = type(self)()
        for child in self._children:
            clone.add(child.clone())
        return clone


class ClauseHandler(ABC):
    """Base handler for clause processing.
    
    This class implements the Chain of Responsibility pattern for
    processing clauses through multiple steps (validation,
    optimization, etc.).
    
    Example:
        ```python
        # Create a processing chain
        validator = ClauseValidator()
        optimizer = ClauseOptimizer()
        executor = ClauseExecutor()
        
        validator.set_next(optimizer).set_next(executor)
        validator.handle(clause)
        ```
    """

    def __init__(self):
        """Initialize handler with no next handler."""
        self._next_handler: Optional['ClauseHandler'] = None

    def set_next(self, handler: 'ClauseHandler') -> 'ClauseHandler':
        """Set the next handler in the chain.
        
        Args:
            handler: The next handler to process clauses.
            
        Returns:
            ClauseHandler: The next handler (for chaining).
        """
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, clause: Clause) -> None:
        """Handle a clause.
        
        Args:
            clause: The clause to process.
        """
        pass