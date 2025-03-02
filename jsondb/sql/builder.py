from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union

from .expressions import Expression, Column, Table, BinaryOperator
from .parameters import ParameterStore

T = TypeVar('T')


@dataclass
class QueryBuilder:
    """Dynamic query builder with parameterization."""

    parameters: ParameterStore = field(default_factory=ParameterStore)
    _tables: Set[Table] = field(default_factory=set)
    _columns: List[Column] = field(default_factory=list)
    _conditions: List[Expression] = field(default_factory=list)
    _joins: List[tuple[Table, Expression]] = field(default_factory=list)
    _group_by: List[Column] = field(default_factory=list)
    _having: Optional[Expression] = None
    _order_by: List[tuple[Column, str]] = field(default_factory=list)
    _limit: Optional[int] = None
    _offset: Optional[int] = None

    def from_(self, table: Union[str, Table, Type[T]]) -> 'QueryBuilder':
        """Add FROM clause."""
        if isinstance(table, str):
            table = Table(table)
        elif isinstance(table, type):
            table = Table(table.__name__.lower())
        self._tables.add(table)
        return self

    def select(self, *columns: Union[str, Column, Expression]) -> 'QueryBuilder':
        """Add columns to SELECT."""
        for col in columns:
            if isinstance(col, str):
                self._columns.append(Column(col))
            elif isinstance(col, (Column, Expression)):
                self._columns.append(col)
        return self

    def where(self, *conditions: Union[Expression, Dict[str, Any]]) -> 'QueryBuilder':
        """Add WHERE conditions with automatic parameterization."""
        for condition in conditions:
            if isinstance(condition, dict):
                # Convert dict to parameterized conditions
                for key, value in condition.items():
                    param = self.parameters.add(value)
                    self._conditions.append(
                        BinaryOperator(Column(key), "=", param)
                    )
            else:
                self._conditions.append(condition)
        return self

    def join(
            self,
            table: Union[str, Table, Type[T]],
            on: Optional[Expression] = None,
            join_type: str = "INNER"
    ) -> 'QueryBuilder':
        """Add JOIN clause."""
        if isinstance(table, str):
            table = Table(table)
        elif isinstance(table, type):
            table = Table(table.__name__.lower())

        if on:
            self._joins.append((table, on))
        return self

    def group_by(self, *columns: Union[str, Column]) -> 'QueryBuilder':
        """Add GROUP BY clause."""
        for col in columns:
            if isinstance(col, str):
                self._group_by.append(Column(col))
            else:
                self._group_by.append(col)
        return self

    def having(self, condition: Expression) -> 'QueryBuilder':
        """Add HAVING clause."""
        self._having = condition
        return self

    def order_by(
            self,
            *columns: Union[str, Column],
            direction: str = "ASC"
    ) -> 'QueryBuilder':
        """Add ORDER BY clause."""
        for col in columns:
            if isinstance(col, str):
                self._order_by.append((Column(col), direction))
            else:
                self._order_by.append((col, direction))
        return self

    def limit(self, limit: int) -> 'QueryBuilder':
        """Add LIMIT clause."""
        self._limit = limit
        return self

    def offset(self, offset: int) -> 'QueryBuilder':
        """Add OFFSET clause."""
        self._offset = offset
        return self

    def build(self) -> tuple[str, Dict[str, Any]]:
        """Build the query and return SQL with parameters."""
        # Build query parts
        parts = []

        # SELECT
        columns = ", ".join(str(col) for col in self._columns) or "*"
        parts.append(f"SELECT {columns}")

        # FROM
        tables = ", ".join(str(table) for table in self._tables)
        parts.append(f"FROM {tables}")

        # JOIN
        for table, condition in self._joins:
            parts.append(f"JOIN {table} ON {condition}")

        # WHERE
        if self._conditions:
            conditions = " AND ".join(str(cond) for cond in self._conditions)
            parts.append(f"WHERE {conditions}")

        # GROUP BY
        if self._group_by:
            groups = ", ".join(str(col) for col in self._group_by)
            parts.append(f"GROUP BY {groups}")

        # HAVING
        if self._having:
            parts.append(f"HAVING {self._having}")

        # ORDER BY
        if self._order_by:
            orders = ", ".join(f"{col} {direction}" for col, direction in self._order_by)
            parts.append(f"ORDER BY {orders}")

        # LIMIT/OFFSET
        if self._limit is not None:
            parts.append(f"LIMIT {self._limit}")
        if self._offset is not None:
            parts.append(f"OFFSET {self._offset}")

        # Build final query
        sql = " ".join(parts)

        # Get parameters
        params = {
            param.name: param.value
            for param in self.parameters.parameters.values()
        }

        return sql, params
