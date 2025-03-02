from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set


@dataclass
class EvaluationContext:
    """Context for secure expression evaluation."""

    # Access control
    allowed_tables: Set[str] = field(default_factory=set)
    allowed_columns: Dict[str, Set[str]] = field(default_factory=dict)
    allowed_functions: Set[str] = field(default_factory=set)

    # Query limits
    max_conditions: int = 20
    max_joins: int = 5
    max_rows: int = 1000
    condition_count: int = 0
    join_count: int = 0

    # Rate limiting
    query_count: int = 0
    last_query_time: Optional[datetime] = None
    max_queries_per_minute: int = 60

    def can_access_column(self, table: Optional[str], column: str) -> bool:
        """Check if column access is allowed."""
        if table is None:
            return True
        return (
                table in self.allowed_tables and
                column in self.allowed_columns.get(table, set())
        )

    def can_access_function(self, name: str) -> bool:
        """Check if function access is allowed."""
        return name in self.allowed_functions

    def get_column_value(self, table: Optional[str], column: str) -> Any:
        """Get column value with access control."""
        if not self.can_access_column(table, column):
            raise ValueError(f"Access denied to {table}.{column}")
        # Implementation would get actual value
        pass

    def evaluate_operator(self, op: str, left: Any, right: Any) -> Any:
        """Evaluate operator safely."""
        # Track condition count for complex queries
        if op in {'AND', 'OR'}:
            self.condition_count += 1
            if self.condition_count > self.max_conditions:
                raise ValueError("Too many conditions")

        # Safe operator evaluation
        if op == '=':
            return left == right
        elif op == '!=':
            return left != right
        elif op == '<':
            return left < right
        elif op == '<=':
            return left <= right
        elif op == '>':
            return left > right
        elif op == '>=':
            return left >= right
        elif op == 'AND':
            return left and right
        elif op == 'OR':
            return left or right
        elif op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            if right == 0:
                raise ValueError("Division by zero")
            return left / right
        else:
            raise ValueError(f"Unknown operator: {op}")

    def evaluate_function(self, name: str, args: List[Any]) -> Any:
        """Evaluate function safely."""
        if not self.can_access_function(name):
            raise ValueError(f"Access denied to function {name}")

        # Built-in functions
        if name == 'COUNT':
            return len(args[0]) if args else 0
        elif name == 'SUM':
            return sum(args[0]) if args else 0
        elif name == 'AVG':
            values = args[0] if args else []
            return sum(values) / len(values) if values else 0
        elif name == 'MIN':
            return min(args[0]) if args else None
        elif name == 'MAX':
            return max(args[0]) if args else None
        else:
            raise ValueError(f"Unknown function: {name}")

    def check_rate_limit(self) -> None:
        """Check and update rate limit."""
        now = datetime.now()

        # Reset counter if it's been more than a minute
        if (self.last_query_time and
                (now - self.last_query_time).total_seconds() > 60):
            self.query_count = 0

        # Update counter
        self.query_count += 1
        self.last_query_time = now

        if self.query_count > self.max_queries_per_minute:
            raise ValueError("Rate limit exceeded")
