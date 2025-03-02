from typing import List, Optional, Set

from .execution import (
    TableScanPlan, IndexScanPlan, JoinPlan,
    ProjectPlan
)
from .interfaces import IOptimizer, IExecutionPlan, IPredicate


class QueryOptimizer(IOptimizer):
    """Optimizes query execution plans."""

    def optimize(self, plan: IExecutionPlan) -> IExecutionPlan:
        """Optimize an execution plan."""
        # Apply optimization rules
        plan = self._push_down_predicates(plan)
        plan = self._choose_join_order(plan)
        plan = self._choose_access_paths(plan)
        plan = self._merge_projections(plan)
        return plan

    def _push_down_predicates(self, plan: IExecutionPlan) -> IExecutionPlan:
        """Push predicates down the plan tree."""
        if isinstance(plan, JoinPlan):
            # Split join condition into parts that can be pushed down
            left_pred, right_pred, join_pred = self._split_join_condition(
                plan.condition
            )

            # Recursively optimize and push predicates
            plan.left = self._push_down_predicates(plan.left)
            plan.right = self._push_down_predicates(plan.right)

            # Add pushed-down predicates
            if left_pred:
                plan.left = self._add_predicate(plan.left, left_pred)
            if right_pred:
                plan.right = self._add_predicate(plan.right, right_pred)

            # Update join condition
            plan.condition = join_pred

        return plan

    def _choose_join_order(self, plan: IExecutionPlan) -> IExecutionPlan:
        """Choose the optimal join order."""
        if isinstance(plan, JoinPlan):
            # Collect join graph
            tables = self._collect_tables(plan)
            predicates = self._collect_predicates(plan)

            # Use dynamic programming to find optimal join order
            best_plan = self._dp_join_order(tables, predicates)
            return best_plan

        return plan

    def _choose_access_paths(self, plan: IExecutionPlan) -> IExecutionPlan:
        """Choose optimal access paths (table scan vs index)."""
        if isinstance(plan, TableScanPlan):
            # Check if we can use an index
            best_index = self._find_best_index(
                plan.table,
                plan.predicate if hasattr(plan, 'predicate') else None
            )

            if best_index:
                return IndexScanPlan(
                    table=plan.table,
                    index=best_index,
                    columns=plan.columns,
                    key_range=self._compute_key_range(plan.predicate)
                )

        return plan

    def _merge_projections(self, plan: IExecutionPlan) -> IExecutionPlan:
        """Merge consecutive projections."""
        if isinstance(plan, ProjectPlan):
            if isinstance(plan.input_plan, ProjectPlan):
                # Merge the projections
                return ProjectPlan(
                    input_plan=plan.input_plan.input_plan,
                    expressions=self._compose_projections(
                        plan.expressions,
                        plan.input_plan.expressions
                    )
                )

        return plan

    def _split_join_condition(self, condition: IPredicate) -> tuple[
        Optional[IPredicate],
        Optional[IPredicate],
        Optional[IPredicate]
    ]:
        """Split a join condition into parts."""
        # Implementation would analyze the condition and split it
        pass

    def _add_predicate(
            self,
            plan: IExecutionPlan,
            predicate: IPredicate
    ) -> IExecutionPlan:
        """Add a predicate to a plan."""
        if isinstance(plan, TableScanPlan):
            return TableScanPlan(
                table=plan.table,
                columns=plan.columns,
                predicate=self._merge_predicates(plan.predicate, predicate)
            )
        # Handle other plan types
        return plan

    def _collect_tables(self, plan: IExecutionPlan) -> Set[str]:
        """Collect all tables referenced in a plan."""
        tables = set()

        if isinstance(plan, (TableScanPlan, IndexScanPlan)):
            tables.add(plan.table)
        elif isinstance(plan, JoinPlan):
            tables.update(self._collect_tables(plan.left))
            tables.update(self._collect_tables(plan.right))

        return tables

    def _collect_predicates(self, plan: IExecutionPlan) -> List[IPredicate]:
        """Collect all predicates in a plan."""
        predicates = []

        if isinstance(plan, (TableScanPlan, IndexScanPlan)):
            if hasattr(plan, 'predicate') and plan.predicate:
                predicates.append(plan.predicate)
        elif isinstance(plan, JoinPlan):
            predicates.extend(self._collect_predicates(plan.left))
            predicates.extend(self._collect_predicates(plan.right))
            predicates.append(plan.condition)

        return predicates

    def _dp_join_order(
            self,
            tables: Set[str],
            predicates: List[IPredicate]
    ) -> IExecutionPlan:
        """Use dynamic programming to find optimal join order."""
        # Implementation would use dynamic programming to optimize join order
        pass

    def _find_best_index(
            self,
            table: str,
            predicate: Optional[IPredicate]
    ) -> Optional[str]:
        """Find the best index for a table and predicate."""
        # Implementation would analyze available indexes and choose the best one
        pass

    def _compute_key_range(
            self,
            predicate: Optional[IPredicate]
    ) -> tuple:
        """Compute key range for an index scan."""
        # Implementation would analyze predicate to determine key range
        pass

    def _compose_projections(
            self,
            outer: List[IPredicate],
            inner: List[IPredicate]
    ) -> List[IPredicate]:
        """Compose two sets of projections."""
        # Implementation would combine projections efficiently
        pass

    def _merge_predicates(
            self,
            pred1: Optional[IPredicate],
            pred2: Optional[IPredicate]
    ) -> IPredicate:
        """Merge two predicates."""
        # Implementation would combine predicates efficiently
        pass
