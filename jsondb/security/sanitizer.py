import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..sql.expression import Expression, Literal, Column


class ExpressionSanitizer:
    """Sanitizes expressions to prevent SQL injection."""

    SAFE_IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

    @classmethod
    def sanitize(cls, expr: Expression) -> Expression:
        """Sanitize an expression."""
        return expr.accept(cls())

    def visit_literal(self, literal: Literal) -> Literal:
        """Sanitize a literal value."""
        value = literal.value

        if isinstance(value, str):
            # Prevent SQL injection in strings
            value = self._sanitize_string(value)
        elif isinstance(value, (int, float, bool)):
            # Numeric and boolean values are safe
            pass
        elif isinstance(value, datetime):
            # Datetime objects are safe
            pass
        elif value is None:
            # None is safe
            pass
        else:
            # Reject unknown types
            raise ValueError(f"Unsupported literal type: {type(value)}")

        return Literal(value)

    def visit_column(self, column: Column) -> Column:
        """Sanitize a column reference."""
        # Validate table name
        if column.table and not self._is_safe_identifier(column.table):
            raise ValueError(f"Invalid table name: {column.table}")

        # Validate column name
        if not self._is_safe_identifier(column.name):
            raise ValueError(f"Invalid column name: {column.name}")

        return column

    def _sanitize_string(self, value: str) -> str:
        """Sanitize a string value."""
        # Remove null bytes
        value = value.replace('\0', '')

        # Escape special characters
        value = value.replace("'", "''")
        value = value.replace("\\", "\\\\")

        return value

    def _is_safe_identifier(self, name: str) -> bool:
        """Check if an identifier is safe."""
        return bool(self.SAFE_IDENTIFIER_PATTERN.match(name))


class QuerySanitizer:
    """Sanitizes complete queries."""

    def __init__(self):
        self._expr_sanitizer = ExpressionSanitizer()

    def sanitize_select(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize a SELECT query."""
        return {
            'columns': self._sanitize_columns(query.get('columns', [])),
            'from': self._sanitize_table(query.get('from')),
            'where': self._sanitize_where(query.get('where')),
            'group_by': self._sanitize_columns(query.get('group_by', [])),
            'having': self._sanitize_where(query.get('having')),
            'order_by': self._sanitize_order_by(query.get('order_by', [])),
            'limit': self._sanitize_limit(query.get('limit')),
            'offset': self._sanitize_limit(query.get('offset'))
        }

    def _sanitize_columns(self, columns: List[Union[str, Expression]]) -> List[Union[str, Expression]]:
        """Sanitize column references."""
        return [
            self._expr_sanitizer.sanitize(col) if isinstance(col, Expression)
            else self._sanitize_column_name(col)
            for col in columns
        ]

    def _sanitize_table(self, table: Optional[str]) -> Optional[str]:
        """Sanitize a table name."""
        if table and not self._expr_sanitizer._is_safe_identifier(table):
            raise ValueError(f"Invalid table name: {table}")
        return table

    def _sanitize_where(self, condition: Optional[Expression]) -> Optional[Expression]:
        """Sanitize a WHERE/HAVING condition."""
        if condition:
            return self._expr_sanitizer.sanitize(condition)
        return None

    def _sanitize_order_by(self, order_by: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sanitize ORDER BY clause."""
        return [{
            'column': self._expr_sanitizer.sanitize(item['column']),
            'direction': item['direction'].upper() if item['direction'] in ('ASC', 'DESC') else 'ASC'
        } for item in order_by]

    def _sanitize_limit(self, value: Optional[int]) -> Optional[int]:
        """Sanitize LIMIT/OFFSET value."""
        if value is not None:
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"Invalid limit/offset value: {value}")
        return value

    def _sanitize_column_name(self, name: str) -> str:
        """Sanitize a column name."""
        if not self._expr_sanitizer._is_safe_identifier(name):
            raise ValueError(f"Invalid column name: {name}")
        return name
