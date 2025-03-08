from dataclasses import dataclass


@dataclass
class SecurityContext:
    """Security context for query execution."""


class SecurityError(Exception):
    """Raised for security violations."""
    pass
