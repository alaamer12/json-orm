from typing import Any, List, Optional, Type, TypeVar, Union, Dict, overload
from datetime import datetime
from .sql.statement.select import SelectStatement
from .sql.expression import Expression, Column, Function
from .sql.processor.chain import ClauseProcessingBuilder
from .sql.parameters import ParameterStore, Parameter
from .sql.builder import QueryBuilder

T = TypeVar('T')


class Query:
    """Base query class for fluent interface."""

    def __init__(self):
        self._chain = (ClauseProcessingBuilder()
                       .add_select_handler()
                       .add_where_handler()
                       .add_join_handler()
                       .add_group_by_handler()
                       .add_having_handler()
                       .add_order_by_handler()
                       .add_limit_handler()
                       .build())
        self._params = ParameterStore()
        self._builder = QueryBuilder(parameters=self._params)

    def _process(self, statement: Any) -> None:
        self._chain.process(statement)

    def param(self, value: Any, type_hint: Optional[type] = None) -> Parameter:
        """Create a new parameter."""
        return self._params.add(value, type_hint)


class Select(Query):
    """SELECT query builder with fluent interface."""

    @overload
    def __init__(self, model: Type[T]):
        ...

    @overload
    def __init__(self, *columns: Union[Column, Function]):
        ...

    def __init__(self, *args):
        super().__init__()

        # Handle different initialization cases
        if len(args) == 1 and isinstance(args[0], type):
            # select(User)
            model = args[0]
            self._builder.from_(model)
            # Auto-select all columns from model
            self._builder.select(*self._get_model_columns(model))
        else:
            # select(User.id, User.name)
            self._builder.select(*args)

    def where(self, *conditions: Union[Expression, Dict[str, Any]]) -> 'Select':
        """Add WHERE conditions with parameter support."""
        self._builder.where(*conditions)
        return self

    def join(self, target: Any, condition: Optional[Expression] = None) -> 'Select':
        """Add JOIN clause."""
        self._builder.join(target, condition)
        return self

    def group_by(self, *columns: Column) -> 'Select':
        """Add GROUP BY clause."""
        self._builder.group_by(*columns)
        return self

    def having(self, condition: Expression) -> 'Select':
        """Add HAVING clause."""
        self._builder.having(condition)
        return self

    def order_by(self, *columns: Union[Column, Function]) -> 'Select':
        """Add ORDER BY clause."""
        self._builder.order_by(*columns)
        return self

    def limit(self, limit: int) -> 'Select':
        """Add LIMIT clause."""
        self._builder.limit(limit)
        return self

    def offset(self, offset: int) -> 'Select':
        """Add OFFSET clause."""
        self._builder.offset(offset)
        return self

    def options(self, *options: Any) -> 'Select':
        """Add query options (e.g., joinedload)."""
        for option in options:
            self._builder.options().add_option(option)
        return self

    def paginate(self, page: int = 1, per_page: int = 10) -> 'Select':
        """Add pagination."""
        offset = (page - 1) * per_page
        return self.limit(per_page).offset(offset)

    def build(self) -> tuple[SelectStatement, Dict[str, Any]]:
        """Build and return the final statement with parameters."""
        statement = self._builder.build()
        self._process(statement)
        return statement, self._params.parameters

    def _get_model_columns(self, model: Type[T]) -> List[Column]:
        """Get all columns from a model."""
        # Implementation depends on model system
        pass


# Helper functions to match example.py
def select(*args: Any) -> Select:
    """Create a new SELECT query."""
    return Select(*args)


def update(model: Type[T]) -> 'Update':
    """Create a new UPDATE query."""
    return Update(model)


def delete(model: Type[T]) -> 'Delete':
    """Create a new DELETE query."""
    return Delete(model)


def param(value: Any, type_hint: Optional[type] = None) -> Parameter:
    """Create a new query parameter."""
    return ParameterStore().add(value, type_hint)


def and_(*conditions: Expression) -> Expression:
    """Combine conditions with AND."""
    from .sql.expression import And
    return And(*conditions)


def or_(*conditions: Expression) -> Expression:
    """Combine conditions with OR."""
    from .sql.expression import Or
    return Or(*conditions)


def desc(column: Union[Column, Function]) -> Expression:
    """Order by column in descending order."""
    from .sql.expression import Desc
    return Desc(column)


def func() -> Any:
    """Access SQL functions."""
    from .sql.function import Functions
    return Functions()


def relationship(*args: Any, **kwargs: Any) -> Any:
    """Define a relationship."""
    from .model.relationship import Relationship
    return Relationship(*args, **kwargs)


def joinedload(*args: Any) -> Any:
    """Eager load relationships."""
    from .model.loader import JoinedLoader
    return JoinedLoader(*args)
