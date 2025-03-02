from typing import List

from .base import Clause, ClauseVisitor, ClauseBuilder, ClauseHandler
from ..expression import Expression


class SelectClause(Clause):
    """SELECT clause in a SELECT statement."""

    def __init__(self):
        self._columns: List[Expression] = []
        self._distinct: bool = False

    def add_column(self, column: Expression) -> None:
        self._columns.append(column)

    def set_distinct(self, distinct: bool) -> None:
        self._distinct = distinct

    def accept(self, visitor: ClauseVisitor) -> None:
        visitor.visit(self)

    def validate(self) -> bool:
        return len(self._columns) > 0

    def clone(self) -> 'SelectClause':
        clone = SelectClause()
        clone._columns = [col.clone() for col in self._columns]
        clone._distinct = self._distinct
        return clone


class SelectClauseBuilder(ClauseBuilder['SelectClause']):
    """Builder for SELECT clauses."""

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self._clause = SelectClause()

    def add_column(self, column: Expression) -> 'SelectClauseBuilder':
        self._clause.add_column(column)
        return self

    def set_distinct(self, distinct: bool) -> 'SelectClauseBuilder':
        self._clause.set_distinct(distinct)
        return self

    def get_result(self) -> SelectClause:
        clause = self._clause
        self.reset()
        return clause


class SelectClauseHandler(ClauseHandler):
    """Handler for SELECT clauses."""

    def handle(self, clause: Clause) -> None:
        if isinstance(clause, SelectClause):
            # Handle SELECT clause
            self._process_select(clause)
        self._handle_next(clause)

    def _process_select(self, clause: SelectClause) -> None:
        # Implementation of SELECT clause processing
        pass
