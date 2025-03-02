from dataclasses import dataclass, field
from typing import List, Optional, Union

from .expressions import Expression, Column, Table


@dataclass
class WhereClause:
    """Represents a WHERE clause in a SQL statement."""
    conditions: List[Expression] = field(default_factory=list)

    def add_condition(self, condition: Expression) -> None:
        self.conditions.append(condition)


@dataclass
class JoinClause:
    """Represents a JOIN clause in a SQL statement."""
    table: Table
    condition: Expression
    join_type: str = "INNER"  # INNER, LEFT, RIGHT, FULL


@dataclass
class OrderByClause:
    """Represents an ORDER BY clause in a SQL statement."""
    clauses: List[Union[Column, Expression]] = field(default_factory=list)
    directions: List[str] = field(default_factory=list)  # ASC or DESC


@dataclass
class GroupByClause:
    """Represents a GROUP BY clause in a SQL statement."""
    columns: List[Column] = field(default_factory=list)


@dataclass
class HavingClause:
    """Represents a HAVING clause in a SQL statement."""
    condition: Expression


@dataclass
class LimitClause:
    """Represents a LIMIT clause in a SQL statement."""
    count: int
    offset: Optional[int] = None


@dataclass
class SetClause:
    """Represents a SET clause in an UPDATE statement."""
    assignments: List[tuple[Column, Expression]] = field(default_factory=list)


@dataclass
class ValuesClause:
    """Represents a VALUES clause in an INSERT statement."""
    columns: List[Column]
    values: List[List[Expression]]
