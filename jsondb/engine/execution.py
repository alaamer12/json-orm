from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional

from .interfaces import (
    IExecutionPlan, IExecutionContext, IResultSet, IPredicate, IExpression
)


class ExecutionPlan(IExecutionPlan):
    """Base class for execution plans."""

    def execute(self, context: IExecutionContext) -> IResultSet:
        raise NotImplementedError


class TableScanPlan(ExecutionPlan):
    """Full table scan execution plan."""

    def __init__(
            self,
            table: str,
            columns: List[str],
            predicate: Optional[IPredicate] = None
    ):
        self.table = table
        self.columns = columns
        self.predicate = predicate

    def execute(self, context: IExecutionContext) -> IResultSet:
        storage = context.get_storage()
        return storage.read(self.table, self.columns, self.predicate)

class JoinPlan(ExecutionPlan):
    """Join execution plan."""



class AggregatePlan(ExecutionPlan):
    """Aggregation execution plan."""


class SortPlan(ExecutionPlan):
    """Sort execution plan."""

class ProjectPlan(ExecutionPlan):
    """Projection execution plan."""


class LimitPlan(ExecutionPlan):
    """Limit execution plan."""



class InsertPlan(ExecutionPlan):
    """Insert execution plan."""



class UpdatePlan(ExecutionPlan):
    """Update execution plan."""


class DeletePlan(ExecutionPlan):
    """Delete execution plan."""



class SingleRowResult(IResultSet):
    """Result set containing a single row."""
