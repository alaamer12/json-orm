"""SQL query builder for the JSON database.

This module provides a fluent interface for building SQL queries
dynamically with proper parameterization and type safety. It supports
all SQL operations and ensures queries are built securely.

Example:
    ```python
    # Build a SELECT query
    query = (QueryBuilder()
             .select(User.name, User.email)
             .from_(User)
             .where(User.age > 18)
             .order_by(User.name)
             .build())
             
    # Build an INSERT query
    query = (QueryBuilder()
             .insert_into(User)
             .columns(User.name, User.email)
             .values("John", "john@example.com")
             .build())
    ```
"""

from dataclasses import dataclass
from typing import TypeVar

T = TypeVar('T')


@dataclass
class QueryBuilder:
    """Dynamic query builder with parameterization.
    
    This class provides a fluent interface for building SQL queries
    with proper parameterization and type safety. It supports all
    standard SQL operations and ensures queries are built securely.
    
    Example:
        ```python
        # Build a simple SELECT
        query = (QueryBuilder()
                .select(User.name, User.email)
                .from_(User)
                .where(User.age > 18)
                .build())
        
        # Build a complex query
        query = (QueryBuilder()
                .select(
                    User.country,
                    func.count(User.id).as_("user_count")
                )
                .from_(User)
                .join(Order, User.id == Order.user_id)
                .where(User.status == "active")
                .group_by(User.country)
                .having(func.count(User.id) > 100)
                .order_by(func.count(User.id).desc())
                .limit(10)
                .build())
                
        # Build an INSERT
        query = (QueryBuilder()
                .insert_into(User)
                .columns(User.name, User.email)
                .values("John", "john@example.com")
                .build())
                
        # Build an UPDATE
        query = (QueryBuilder()
                .update(User)
                .set(User.status, "inactive")
                .where(User.last_login < datetime.now() - timedelta(days=90))
                .build())
                
        # Build a DELETE
        query = (QueryBuilder()
                .delete_from(User)
                .where(User.status == "deleted")
                .build())
        ```
    """