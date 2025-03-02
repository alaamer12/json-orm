from typing import List, Optional, Any

from .execution import (
    TableScanPlan, JoinPlan,
    AggregatePlan, SortPlan, ProjectPlan,
    InsertPlan, UpdatePlan, DeletePlan
)
from .interfaces import (
    IStatementVisitor,
    ISelectStatement, IInsertStatement,
    IUpdateStatement, IDeleteStatement,
    IExecutionPlan
)


class QueryPlanner(IStatementVisitor):
    """Plans query execution strategies."""

    def visit_select(self, select: ISelectStatement) -> IExecutionPlan:
        """Create execution plan for SELECT statement."""
        # Start with base table access
        plan = self._create_base_access(select)

        # Add joins if any
        if select.joins:
            plan = self._add_joins(plan, select.joins)

        # Add where clause
        if select.where:
            plan = self._add_where(plan, select.where)

        # Add group by and aggregates
        if select.group_by or select.aggregates:
            plan = self._add_aggregation(plan, select)

        # Add having clause
        if select.having:
            plan = self._add_having(plan, select.having)

        # Add order by
        if select.order_by:
            plan = self._add_sorting(plan, select.order_by)

        # Add projection
        plan = self._add_projection(plan, select.columns)

        # Add limit/offset
        if select.limit:
            plan = self._add_limit(plan, select.limit, select.offset)

        return plan

    def visit_insert(self, insert: IInsertStatement) -> IExecutionPlan:
        """Create execution plan for INSERT statement."""
        return InsertPlan(
            table=insert.table.name,
            columns=[col.name for col in insert.columns],
            values=insert.values
        )

    def visit_update(self, update: IUpdateStatement) -> IExecutionPlan:
        """Create execution plan for UPDATE statement."""
        return UpdatePlan(
            table=update.table.name,
            updates=update.updates,
            predicate=update.where
        )

    def visit_delete(self, delete: IDeleteStatement) -> IExecutionPlan:
        """Create execution plan for DELETE statement."""
        return DeletePlan(
            table=delete.table.name,
            predicate=delete.where
        )

    def _create_base_access(self, select: ISelectStatement) -> IExecutionPlan:
        """Create base table access plan."""
        # Check if we can use an index
        if select.where:
            index_plan = self._try_index_access(
                select.from_table.name,
                select.where
            )
            if index_plan:
                return index_plan

        # Fall back to table scan
        return TableScanPlan(
            table=select.from_table.name,
            columns=self._get_required_columns(select)
        )

    def _add_joins(
            self,
            plan: IExecutionPlan,
            joins: List[Any]
    ) -> IExecutionPlan:
        """Add join operations to plan."""
        for join in joins:
            right_plan = self._create_base_access(join.table)
            plan = JoinPlan(
                left=plan,
                right=right_plan,
                condition=join.condition
            )
        return plan

    def _add_where(
            self,
            plan: IExecutionPlan,
            where: Any
    ) -> IExecutionPlan:
        """Add where clause to plan."""
        if isinstance(plan, TableScanPlan):
            return TableScanPlan(
                table=plan.table,
                columns=plan.columns,
                predicate=where
            )
        return plan

    def _add_aggregation(
            self,
            plan: IExecutionPlan,
            select: ISelectStatement
    ) -> IExecutionPlan:
        """Add aggregation to plan."""
        return AggregatePlan(
            input_plan=plan,
            group_by=[col.name for col in select.group_by],
            aggregates=[(agg.func, agg.expr) for agg in select.aggregates]
        )

    def _add_having(
            self,
            plan: IExecutionPlan,
            having: Any
    ) -> IExecutionPlan:
        """Add having clause to plan."""
        if isinstance(plan, AggregatePlan):
            plan.having = having
        return plan

    def _add_sorting(
            self,
            plan: IExecutionPlan,
            order_by: List[Any]
    ) -> IExecutionPlan:
        """Add sorting to plan."""
        return SortPlan(
            input_plan=plan,
            sort_columns=[(col.name, direction) for col, direction in order_by]
        )

    def _add_projection(
            self,
            plan: IExecutionPlan,
            columns: List[Any]
    ) -> IExecutionPlan:
        """Add projection to plan."""
        return ProjectPlan(
            input_plan=plan,
            expressions=columns
        )

    def _add_limit(
            self,
            plan: IExecutionPlan,
            limit: int,
            offset: Optional[int]
    ) -> IExecutionPlan:
        """Add limit/offset to plan."""
        from .execution import LimitPlan
        return LimitPlan(
            input_plan=plan,
            limit=limit,
            offset=offset
        )

    def _try_index_access(
            self,
            table: str,
            where: Any
    ) -> Optional[IExecutionPlan]:
        """Try to create an index access plan."""
        # Implementation would analyze where clause and available indexes
        pass

    def _get_required_columns(
            self,
            select: ISelectStatement
    ) -> List[str]:
        """Get list of columns required for query."""
        columns = set()

        # Add selected columns
        for col in select.columns:
            if hasattr(col, 'name'):
                columns.add(col.name)

        # Add columns used in where clause
        if select.where:
            columns.update(self._extract_columns(select.where))

        # Add columns used in joins
        for join in select.joins:
            columns.update(self._extract_columns(join.condition))

        # Add group by columns
        if select.group_by:
            for col in select.group_by:
                columns.add(col.name)

        # Add order by columns
        if select.order_by:
            for col, _ in select.order_by:
                columns.add(col.name)

        return list(columns)

    def _extract_columns(self, expr: Any) -> List[str]:
        """Extract column names from an expression."""
        # Implementation would traverse expression tree
        pass
