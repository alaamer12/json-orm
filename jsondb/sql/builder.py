from dataclasses import dataclass
from typing import TypeVar

T = TypeVar('T')


@dataclass
class QueryBuilder:
    """Dynamic query builder with parameterization."""