import json
from contextlib import contextmanager
from typing import Any, Dict, List, Type, TypeVar

from .model import Model

T = TypeVar('T')


class Database:
    """Main database class."""

    def __init__(self, filename: str):
        self.filename = filename
        self._data: Dict[str, List[Dict[str, Any]]] = {}
        self._load()

    def _load(self):
        """Load data from file."""
        try:
            with open(self.filename, 'r') as f:
                self._data = json.load(f)
        except FileNotFoundError:
            self._data = {}

    def _save(self):
        """Save data to file."""
        with open(self.filename, 'w') as f:
            json.dump(self._data, f, indent=2)

    @contextmanager
    def transaction(self):
        """Transaction context manager."""
        try:
            yield
            self._save()
        except Exception:
            # Rollback by reloading
            self._load()
            raise

    def add(self, model: Model):
        """Add a model to the database."""
        table = model.__class__.__name__.lower()
        if table not in self._data:
            self._data[table] = []

        # Handle primary key
        pk_field = model.get_primary_key()
        if pk_field and getattr(model, pk_field.name) is None:
            # Auto-increment
            if self._data[table]:
                max_id = max(row[pk_field.name] for row in self._data[table])
                setattr(model, pk_field.name, max_id + 1)
            else:
                setattr(model, pk_field.name, 1)

        self._data[table].append(model.to_dict())

    def bulk_insert(self, model_class: Type[Model], data: List[Dict[str, Any]]):
        """Insert multiple records."""
        table = model_class.__name__.lower()
        if table not in self._data:
            self._data[table] = []

        # Handle primary keys
        pk_field = model_class.get_primary_key()
        if pk_field:
            start_id = 1
            if self._data[table]:
                start_id = max(row[pk_field.name] for row in self._data[table]) + 1

            for i, row in enumerate(data):
                if pk_field.name not in row:
                    row[pk_field.name] = start_id + i

        # Convert to models and back to ensure validation
        models = [model_class(**row) for row in data]
        self._data[table].extend(model.to_dict() for model in models)
        self._save()

    def migrate_record(self, model: Model, engine: Any):
        """Migrate a record to SQLModel."""
        # This would be implemented based on SQLModel's API
        pass
