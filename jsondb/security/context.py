from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, Set


@dataclass
class SecurityContext:
    """Security context for query execution."""

    # Authentication
    user_id: Optional[str] = None
    roles: Set[str] = None

    # Authorization
    allowed_tables: Set[str] = None
    allowed_operations: Set[str] = None

    # Rate limiting
    last_query_time: Optional[datetime] = None
    query_count: int = 0
    max_queries_per_minute: int = 60

    # Resource limits
    max_rows: int = 1000
    max_execution_time: int = 30  # seconds

    def __post_init__(self):
        self.roles = self.roles or set()
        self.allowed_tables = self.allowed_tables or set()
        self.allowed_operations = self.allowed_operations or set()

    def can_access_table(self, table: str) -> bool:
        """Check if user can access a table."""
        return (
                'admin' in self.roles or
                table in self.allowed_tables
        )

    def can_perform_operation(self, operation: str) -> bool:
        """Check if user can perform an operation."""
        return (
                'admin' in self.roles or
                operation in self.allowed_operations
        )

    def check_rate_limit(self) -> bool:
        """Check if user has exceeded rate limit."""
        now = datetime.now()

        # Reset counter if it's been more than a minute
        if (self.last_query_time and
                (now - self.last_query_time).total_seconds() > 60):
            self.query_count = 0

        # Update counter
        self.query_count += 1
        self.last_query_time = now

        return self.query_count <= self.max_queries_per_minute

    def validate_query(self, query: Any) -> None:
        """Validate a query against security context."""
        # Check authentication
        if not self.user_id:
            raise SecurityError("Authentication required")

        # Check rate limit
        if not self.check_rate_limit():
            raise SecurityError("Rate limit exceeded")

        # Check operation permissions
        operation = self._get_query_operation(query)
        if not self.can_perform_operation(operation):
            raise SecurityError(f"Operation '{operation}' not allowed")

        # Check table permissions
        tables = self._get_query_tables(query)
        for table in tables:
            if not self.can_access_table(table):
                raise SecurityError(f"Access to table '{table}' not allowed")

    def _get_query_operation(self, query: Any) -> str:
        """Get the operation type from a query."""
        # Implementation depends on query type
        pass

    def _get_query_tables(self, query: Any) -> Set[str]:
        """Get all tables referenced in a query."""
        # Implementation depends on query type
        pass


class SecurityError(Exception):
    """Raised for security violations."""
    pass
