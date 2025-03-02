from typing import List, Optional

from .base import Statement, StatementVisitor, StatementBuilder, StatementDirector
from ..clause.base import Clause
from ..clause.groupby import GroupByClause, GroupByClauseBuilder
from ..clause.having import HavingClause, HavingClauseBuilder
from ..clause.join import JoinClause, JoinClauseBuilder
from ..clause.limit import LimitClause, LimitClauseBuilder
from ..clause.orderby import OrderByClause, OrderByClauseBuilder
from ..clause.select import SelectClause, SelectClauseBuilder
from ..clause.where import WhereClause, WhereClauseBuilder


class SelectStatement(Statement):
    """Represents a SELECT statement."""

    def __init__(self):
        self._select: Optional[SelectClause] = None
        self._where: Optional[WhereClause] = None
        self._joins: List[JoinClause] = []
        self._group_by: Optional[GroupByClause] = None
        self._having: Optional[HavingClause] = None
        self._order_by: Optional[OrderByClause] = None
        self._limit: Optional[LimitClause] = None

    def accept(self, visitor: StatementVisitor) -> None:
        visitor.visit(self)

    def get_clauses(self) -> List[Clause]:
        clauses = []
        if self._select:
            clauses.append(self._select)
        clauses.extend(self._joins)
        if self._where:
            clauses.append(self._where)
        if self._group_by:
            clauses.append(self._group_by)
        if self._having:
            clauses.append(self._having)
        if self._order_by:
            clauses.append(self._order_by)
        if self._limit:
            clauses.append(self._limit)
        return clauses


class SelectStatementBuilder(StatementBuilder['SelectStatement']):
    """Builder for SELECT statements."""

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self._statement = SelectStatement()
        self._select_builder = SelectClauseBuilder()
        self._where_builder = WhereClauseBuilder()
        self._join_builder = JoinClauseBuilder()
        self._group_by_builder = GroupByClauseBuilder()
        self._having_builder = HavingClauseBuilder()
        self._order_by_builder = OrderByClauseBuilder()
        self._limit_builder = LimitClauseBuilder()

    def select(self) -> SelectClauseBuilder:
        return self._select_builder

    def where(self) -> WhereClauseBuilder:
        return self._where_builder

    def join(self) -> JoinClauseBuilder:
        return self._join_builder

    def group_by(self) -> GroupByClauseBuilder:
        return self._group_by_builder

    def having(self) -> HavingClauseBuilder:
        return self._having_builder

    def order_by(self) -> OrderByClauseBuilder:
        return self._order_by_builder

    def limit(self) -> LimitClauseBuilder:
        return self._limit_builder

    def get_result(self) -> SelectStatement:
        # Build all clauses
        self._statement._select = self._select_builder.get_result()
        self._statement._where = self._where_builder.get_result()
        self._statement._joins.append(self._join_builder.get_result())
        self._statement._group_by = self._group_by_builder.get_result()
        self._statement._having = self._having_builder.get_result()
        self._statement._order_by = self._order_by_builder.get_result()
        self._statement._limit = self._limit_builder.get_result()

        statement = self._statement
        self.reset()
        return statement


class SelectStatementDirector(StatementDirector):
    """Director for SELECT statement construction."""

    def construct(self, builder: SelectStatementBuilder) -> None:
        """Construct a SELECT statement using the builder."""
        # Each clause builder manages its own construction
        builder.select().build()
        builder.where().build()
        builder.join().build()
        builder.group_by().build()
        builder.having().build()
        builder.order_by().build()
        builder.limit().build()
