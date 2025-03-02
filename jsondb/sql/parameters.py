from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from uuid import uuid4


@dataclass
class Parameter:
    """Represents a query parameter."""
    name: str
    value: Any
    type: Optional[type] = None

    @classmethod
    def create(cls, value: Any, type_hint: Optional[type] = None) -> 'Parameter':
        """Create a new parameter with a unique name."""
        return cls(
            name=f"p_{uuid4().hex[:8]}",
            value=value,
            type=type_hint or type(value)
        )


@dataclass
class ParameterStore:
    """Stores and manages query parameters."""
    parameters: Dict[str, Parameter] = field(default_factory=dict)

    def add(self, value: Any, type_hint: Optional[type] = None) -> Parameter:
        """Add a new parameter and return its reference."""
        param = Parameter.create(value, type_hint)
        self.parameters[param.name] = param
        return param

    def get(self, name: str) -> Parameter:
        """Get a parameter by name."""
        return self.parameters[name]

    def clear(self) -> None:
        """Clear all parameters."""
        self.parameters.clear()
