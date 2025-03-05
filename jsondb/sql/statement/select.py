from typing import List, Optional

from .base import Statement, StatementBuilder, StatementDirector
from ..clause.groupby import GroupByClause
from ..clause.having import HavingClause
from ..clause.join import JoinClause
from ..clause.limit import LimitClause
from ..clause.orderby import OrderByClause
from ..clause.select import SelectClause
from ..clause.where import WhereClause


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

class SelectStatementBuilder(StatementBuilder['SelectStatement']):
    """Builder for SELECT statements."""

class SelectStatementDirector(StatementDirector):
    """Director for SELECT statement construction."""
