from typing import List

from .clauses import (
    WhereClause, JoinClause, OrderByClause,
    GroupByClause, HavingClause, LimitClause
)
from .expressions import (
    Expression, Column, Table, Literal, Function,
    BinaryOperator, UnaryOperator
)
from .statements.select import SelectStatement


class SQLParser:
    """Parses SQL statements into statement objects."""

    def parse_select(self, query: str) -> SelectStatement:
        """Parse a SELECT statement."""
        # This would be implemented with a proper SQL parser
        # For now, just a placeholder showing the structure
        pass

    def parse_expression(self, expr_str: str) -> Expression:
        """Parse a SQL expression."""
        pass

    def parse_where_clause(self, clause_str: str) -> WhereClause:
        """Parse a WHERE clause."""
        pass

    def parse_join_clause(self, clause_str: str) -> JoinClause:
        """Parse a JOIN clause."""
        pass


class SQLBuilder:
    """Builds SQL statements from statement objects."""

    def build_select(self, stmt: SelectStatement) -> str:
        """Build a SELECT statement."""
        parts = ["SELECT"]

        if stmt.distinct:
            parts.append("DISTINCT")

        # Add columns
        parts.append(self._build_columns(stmt.columns))

        # Add FROM clause
        if stmt.from_table:
            parts.append(f"FROM {self._build_table(stmt.from_table)}")

        # Add JOIN clauses
        for join in stmt.joins:
            parts.append(self._build_join(join))

        # Add WHERE clause
        if stmt.where:
            parts.append(self._build_where(stmt.where))

        # Add GROUP BY clause
        if stmt.group_by:
            parts.append(self._build_group_by(stmt.group_by))

        # Add HAVING clause
        if stmt.having:
            parts.append(self._build_having(stmt.having))

        # Add ORDER BY clause
        if stmt.order_by:
            parts.append(self._build_order_by(stmt.order_by))

        # Add LIMIT clause
        if stmt.limit:
            parts.append(self._build_limit(stmt.limit))

        return " ".join(parts)

    def _build_columns(self, columns: List[Expression]) -> str:
        """Build the columns part of a SELECT statement."""
        if not columns:
            return "*"
        return ", ".join(self._build_expression(col) for col in columns)

    def _build_table(self, table: Table) -> str:
        """Build a table reference."""
        if table.alias:
            return f"{table.name} AS {table.alias}"
        return table.name

    def _build_expression(self, expr: Expression) -> str:
        """Build a SQL expression."""
        if isinstance(expr, Column):
            if expr.table:
                base = f"{expr.table.name}.{expr.name}"
            else:
                base = expr.name
            if expr.alias:
                return f"{base} AS {expr.alias}"
            return base

        elif isinstance(expr, Literal):
            if isinstance(expr.value, str):
                return f"'{expr.value}'"
            return str(expr.value)

        elif isinstance(expr, Function):
            args = ", ".join(self._build_expression(arg) for arg in expr.arguments)
            return f"{expr.name}({args})"

        elif isinstance(expr, BinaryOperator):
            left = self._build_expression(expr.left)
            right = self._build_expression(expr.right)
            return f"{left} {expr.operator} {right}"

        elif isinstance(expr, UnaryOperator):
            operand = self._build_expression(expr.operand)
            return f"{expr.operator} {operand}"

        raise ValueError(f"Unknown expression type: {type(expr)}")

    def _build_where(self, where: WhereClause) -> str:
        """Build a WHERE clause."""
        conditions = " AND ".join(
            self._build_expression(cond) for cond in where.conditions
        )
        return f"WHERE {conditions}"

    def _build_join(self, join: JoinClause) -> str:
        """Build a JOIN clause."""
        return (
            f"{join.join_type} JOIN {self._build_table(join.table)} "
            f"ON {self._build_expression(join.condition)}"
        )

    def _build_group_by(self, group_by: GroupByClause) -> str:
        """Build a GROUP BY clause."""
        columns = ", ".join(self._build_expression(col) for col in group_by.columns)
        return f"GROUP BY {columns}"

    def _build_having(self, having: HavingClause) -> str:
        """Build a HAVING clause."""
        return f"HAVING {self._build_expression(having.condition)}"

    def _build_order_by(self, order_by: OrderByClause) -> str:
        """Build an ORDER BY clause."""
        parts = []
        for clause, direction in zip(order_by.clauses, order_by.directions):
            expr = self._build_expression(clause)
            parts.append(f"{expr} {direction}")
        return f"ORDER BY {', '.join(parts)}"

    def _build_limit(self, limit: LimitClause) -> str:
        """Build a LIMIT clause."""
        if limit.offset is not None:
            return f"LIMIT {limit.count} OFFSET {limit.offset}"
        return f"LIMIT {limit.count}"
