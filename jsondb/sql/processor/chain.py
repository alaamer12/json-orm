from typing import Optional

from ..clause.base import ClauseHandler
from ..statement.base import Statement


class ClauseProcessingChain:
    """Chain of responsibility for clause processing."""

    def __init__(self):
        self._first_handler: Optional[ClauseHandler] = None
        self._last_handler: Optional[ClauseHandler] = None

    def add_handler(self, handler: ClauseHandler) -> None:
        """Add a handler to the chain."""
        if not self._first_handler:
            self._first_handler = handler
            self._last_handler = handler
        else:
            self._last_handler.set_next(handler)
            self._last_handler = handler

    def process(self, statement: Statement) -> None:
        """Process all clauses in a statement."""
        if not self._first_handler:
            return

        for clause in statement.get_clauses():
            self._first_handler.handle(clause)


class ClauseProcessingBuilder:
    """Builder for clause processing chains."""

    def __init__(self):
        self._chain = ClauseProcessingChain()

    def add_select_handler(self) -> 'ClauseProcessingBuilder':
        from ..clause.select import SelectClauseHandler
        self._chain.add_handler(SelectClauseHandler())
        return self

    def add_where_handler(self) -> 'ClauseProcessingBuilder':
        from ..clause.where import WhereClauseHandler
        self._chain.add_handler(WhereClauseHandler())
        return self

    def add_join_handler(self) -> 'ClauseProcessingBuilder':
        from ..clause.join import JoinClauseHandler
        self._chain.add_handler(JoinClauseHandler())
        return self

    def add_group_by_handler(self) -> 'ClauseProcessingBuilder':
        from ..clause.groupby import GroupByClauseHandler
        self._chain.add_handler(GroupByClauseHandler())
        return self

    def add_having_handler(self) -> 'ClauseProcessingBuilder':
        from ..clause.having import HavingClauseHandler
        self._chain.add_handler(HavingClauseHandler())
        return self

    def add_order_by_handler(self) -> 'ClauseProcessingBuilder':
        from ..clause.orderby import OrderByClauseHandler
        self._chain.add_handler(OrderByClauseHandler())
        return self

    def add_limit_handler(self) -> 'ClauseProcessingBuilder':
        from ..clause.limit import LimitClauseHandler
        self._chain.add_handler(LimitClauseHandler())
        return self

    def build(self) -> ClauseProcessingChain:
        return self._chain
