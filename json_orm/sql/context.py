"""SQL evaluation context for the JSON database.

This module provides context classes that hold state and configuration
for SQL expression and statement evaluation. It ensures secure and
consistent evaluation across the database engine.

Example:
    ```python
    # Create an evaluation context
    context = EvaluationContext(
        parameters={"user_id": 123},
        max_recursion=10,
        timeout_ms=1000
    )
    
    # Use in expression evaluation
    result = expression.evaluate(context)
    ```
"""

from dataclasses import dataclass


@dataclass
class EvaluationContext:
    """Context for secure expression evaluation.
    
    This class provides a secure environment for evaluating SQL
    expressions, with configurable limits and parameters to
    prevent malicious or resource-intensive operations.
    
    Attributes:
        parameters: Dictionary of parameter values for the query.
        max_recursion: Maximum recursion depth for expression evaluation.
        timeout_ms: Maximum time in milliseconds for evaluation.
        
    Example:
        ```python
        # Create context with parameters
        context = EvaluationContext(
            parameters={"min_age": 18, "status": "active"},
            max_recursion=5,
            timeout_ms=500
        )
        
        # Use in expression evaluation
        result = (User.age >= context.parameters["min_age"]).evaluate(context)
        ```
    """