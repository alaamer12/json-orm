from .interfaces import (
    IStatementVisitor
)


class QueryPlanner(IStatementVisitor):
    """Plans query execution strategies."""