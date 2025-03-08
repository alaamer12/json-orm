"""SQL parameter management for the JSON database.

This module provides classes for managing SQL query parameters,
supporting parameterized queries to prevent SQL injection and
improve query performance through parameter reuse.

Example:
    ```python
    # Create a parameter store
    store = ParameterStore()
    
    # Add parameters
    age_param = store.add(18, int)
    name_param = store.add("John%")
    
    # Use in query
    query = select(User).where(
        (User.age > age_param) &
        (User.name.like(name_param))
    )
    ```
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from uuid import uuid4


@dataclass
class Parameter:
    """Represents a query parameter.
    
    This class encapsulates a named parameter value with optional type information.
    Parameters are used to safely inject values into SQL queries.
    
    Attributes:
        name: Unique name for the parameter.
        value: The parameter value.
        type: Optional type hint for the value.
        
    Example:
        ```python
        # Create a parameter directly
        param = Parameter("age", 18, int)
        
        # Create with automatic name
        param = Parameter.create(18, int)
        ```
    """
    name: str
    value: Any
    type: Optional[type] = None

    @classmethod
    def create(cls, value: Any, type_hint: Optional[type] = None) -> 'Parameter':
        """Create a new parameter with a unique name.
        
        This factory method generates a unique parameter name using UUID
        and creates a new Parameter instance.
        
        Args:
            value: The parameter value.
            type_hint: Optional type hint for the value.
            
        Returns:
            Parameter: A new parameter with unique name.
            
        Example:
            ```python
            # Create parameter with automatic name
            param = Parameter.create(18, int)
            assert param.name.startswith("p_")
            ```
        """
        return cls(
            name=f"p_{uuid4().hex[:8]}",
            value=value,
            type=type_hint or type(value)
        )


@dataclass
class ParameterStore:
    """Stores and manages query parameters.
    
    This class provides a central store for query parameters,
    managing their lifecycle and access. It ensures parameter
    uniqueness and proper typing.
    
    Attributes:
        parameters: Dictionary mapping parameter names to Parameter objects.
        
    Example:
        ```python
        # Create store and add parameters
        store = ParameterStore()
        age_param = store.add(18, int)
        name_param = store.add("John")
        
        # Access parameters
        param = store.get(age_param.name)
        assert param.value == 18
        
        # Clear store
        store.clear()
        ```
    """
    parameters: Dict[str, Parameter] = field(default_factory=dict)

    def add(self, value: Any, type_hint: Optional[type] = None) -> Parameter:
        """Add a new parameter and return its reference.
        
        Creates a new parameter with a unique name and stores it.
        
        Args:
            value: The parameter value.
            type_hint: Optional type hint for the value.
            
        Returns:
            Parameter: The newly created parameter.
            
        Example:
            ```python
            store = ParameterStore()
            param = store.add(18, int)
            assert param.value == 18
            assert param.type == int
            ```
        """
        param = Parameter.create(value, type_hint)
        self.parameters[param.name] = param
        return param

    def get(self, name: str) -> Parameter:
        """Get a parameter by name.
        
        Args:
            name: Name of the parameter to retrieve.
            
        Returns:
            Parameter: The parameter with the given name.
            
        Raises:
            KeyError: If no parameter exists with the given name.
            
        Example:
            ```python
            store = ParameterStore()
            param = store.add(18)
            same_param = store.get(param.name)
            assert same_param.value == 18
            ```
        """
        return self.parameters[name]

    def clear(self) -> None:
        """Clear all parameters.
        
        Removes all parameters from the store. Useful when reusing
        the store for a new query.
        
        Example:
            ```python
            store = ParameterStore()
            store.add(18)
            store.add("test")
            store.clear()
            assert len(store.parameters) == 0
            ```
        """
        self.parameters.clear()
