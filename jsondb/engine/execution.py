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


class IndexScanPlan(ExecutionPlan):
    """Index scan execution plan."""

    def __init__(
            self,
            table: str,
            index: str,
            columns: List[str],
            key_range: tuple
    ):
        self.table = table
        self.index = index
        self.columns = columns
        self.key_range = key_range

    def execute(self, context: IExecutionContext) -> IResultSet:
        # Implementation would use index for efficient access
        pass


class JoinPlan(ExecutionPlan):
    """Join execution plan."""

    def __init__(
            self,
            left: ExecutionPlan,
            right: ExecutionPlan,
            condition: IExpression
    ):
        self.left = left
        self.right = right
        self.condition = condition

    def execute(self, context: IExecutionContext) -> IResultSet:
        # Implementation would perform the join operation
        pass


class AggregatePlan(ExecutionPlan):
    """Aggregation execution plan."""

    def __init__(
            self,
            input_plan: ExecutionPlan,
            group_by: List[str],
            aggregates: List[tuple[str, str]]  # (function, column)
    ):
        self.input_plan = input_plan
        self.group_by = group_by
        self.aggregates = aggregates

    def execute(self, context: IExecutionContext) -> IResultSet:
        # Implementation would perform the aggregation
        pass


class SortPlan(ExecutionPlan):
    """Sort execution plan."""

    def __init__(
            self,
            input_plan: ExecutionPlan,
            sort_columns: List[tuple[str, str]]  # (column, direction)
    ):
        self.input_plan = input_plan
        self.sort_columns = sort_columns

    def execute(self, context: IExecutionContext) -> IResultSet:
        # Implementation would perform the sort
        pass


class ProjectPlan(ExecutionPlan):
    """Projection execution plan."""

    def __init__(
            self,
            input_plan: ExecutionPlan,
            expressions: List[IExpression]
    ):
        self.input_plan = input_plan
        self.expressions = expressions

    def execute(self, context: IExecutionContext) -> IResultSet:
        # Implementation would perform the projection
        pass


class LimitPlan(ExecutionPlan):
    """Limit execution plan."""

    def __init__(
            self,
            input_plan: ExecutionPlan,
            limit: int,
            offset: Optional[int] = None
    ):
        self.input_plan = input_plan
        self.limit = limit
        self.offset = offset

    def execute(self, context: IExecutionContext) -> IResultSet:
        # Implementation would apply limit and offset
        pass


class InsertPlan(ExecutionPlan):
    """Insert execution plan."""

    def __init__(
            self,
            table: str,
            columns: List[str],
            values: List[List[Any]]
    ):
        self.table = table
        self.columns = columns
        self.values = values

    def execute(self, context: IExecutionContext) -> IResultSet:
        storage = context.get_storage()
        data = [
            dict(zip(self.columns, row))
            for row in self.values
        ]
        count = storage.write(self.table, data)
        return SingleRowResult({"count": count})


class UpdatePlan(ExecutionPlan):
    """Update execution plan."""

    def __init__(
            self,
            table: str,
            updates: Dict[str, Any],
            predicate: Optional[IPredicate] = None
    ):
        self.table = table
        self.updates = updates
        self.predicate = predicate

    def execute(self, context: IExecutionContext) -> IResultSet:
        storage = context.get_storage()
        count = storage.update(self.table, self.updates, self.predicate)
        return SingleRowResult({"count": count})


class DeletePlan(ExecutionPlan):
    """Delete execution plan."""

    def __init__(
            self,
            table: str,
            predicate: Optional[IPredicate] = None
    ):
        self.table = table
        self.predicate = predicate

    def execute(self, context: IExecutionContext) -> IResultSet:
        storage = context.get_storage()
        count = storage.delete(self.table, self.predicate)
        return SingleRowResult({"count": count})


class SingleRowResult(IResultSet):
    """Result set containing a single row."""

    def __init__(self, row: Dict[str, Any]):
        self.row = row
        self.returned = False

    def next(self) -> Optional[Dict[str, Any]]:
        if self.returned:
            return None
        self.returned = True
        return self.row

    def all(self) -> List[Dict[str, Any]]:
        return [self.row] if not self.returned else []
