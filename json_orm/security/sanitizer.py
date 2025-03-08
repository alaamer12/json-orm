import re


class ExpressionSanitizer:
    """Sanitizes expressions to prevent SQL injection."""

    SAFE_IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')


class QuerySanitizer:
    """Sanitizes complete queries."""
