"""Main database class for the JSON database.

This module provides the main Database class that serves as the entry point
for all database operations. It manages connections, transactions, and
provides a high-level interface for executing queries.

Example:
    ```python
    # Create and use a database
    db = Database("mydb.json")
    
    # Execute queries
    users = db.query(User).where(User.age > 18).all()
    
    # Perform transactions
    with db.transaction():
        db.insert(User(name="John", age=25))
        db.update(User).where(User.status == "inactive").set(status="deleted")
        
    # Use raw SQL
    results = db.execute_sql(
        "SELECT name, COUNT(*) as count "
        "FROM users "
        "GROUP BY country"
    )
    ```
"""

from typing import TypeVar

T = TypeVar('T')


class Database:
    """Main database class.
    
    This class serves as the primary interface to the JSON database.
    It handles all database operations including queries, transactions,
    schema management, and optimization.
    
    Attributes:
        path: Path to the database file.
        max_connections: Maximum number of concurrent connections.
        timeout: Operation timeout in seconds.
        
    Example:
        ```python
        # Create a database
        db = Database(
            path="users.json",
            max_connections=10,
            timeout=30
        )
        
        # Basic queries
        active_users = (
            db.query(User)
            .where(User.status == "active")
            .order_by(User.name)
            .all()
        )
        
        # Complex analytics
        user_stats = (
            db.query(
                User.country,
                func.count(User.id).as_("user_count"),
                func.avg(User.age).as_("avg_age")
            )
            .join(Order)
            .where(User.status == "active")
            .group_by(User.country)
            .having(func.count(User.id) > 100)
            .all()
        )
        
        # Transactions
        with db.transaction():
            # Insert data
            user = User(name="John", age=25)
            db.insert(user)
            
            # Update data
            db.update(User)
            .where(User.age < 18)
            .set(status="junior")
            
            # Delete data
            db.delete(User)
            .where(User.status == "inactive")
            
        # Schema management
        db.create_table(User)
        db.add_index(User.email, unique=True)
        db.add_foreign_key(Order.user_id, User.id)
        
        # Optimization
        db.analyze()
        db.vacuum()
        db.optimize_indexes()
        ```
    """
