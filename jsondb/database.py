from pathlib import Path
from typing import Dict, List, Optional, Type, TypeVar, Any
from contextlib import contextmanager
import json

from .model import Model
from .storage import ChunkManager
from .index import IndexManager
from .transaction import TransactionManager
from .exceptions import JsonDBError

T = TypeVar("T", bound=Model)

class Database:
    def __init__(
        self, 
        path: str, 
        chunk_size: int = 1000,
        create_if_missing: bool = True
    ):
        self.base_path = Path(path)
        self._setup_directories(create_if_missing)
        
        self.chunk_manager = ChunkManager(chunk_size)
        self.index_manager = IndexManager(self.index_path)
        self.transaction_manager = TransactionManager(self.meta_path)
        
        self._initialize_db()
    
    def _setup_directories(self, create_if_missing: bool) -> None:
        """Setup database directory structure."""
        self.data_path = self.base_path / "data"
        self.index_path = self.base_path / "indexes"
        self.meta_path = self.base_path / "meta"
        
        if create_if_missing:
            self.data_path.mkdir(parents=True, exist_ok=True)
            self.index_path.mkdir(parents=True, exist_ok=True)
            self.meta_path.mkdir(parents=True, exist_ok=True)
    
    def _initialize_db(self) -> None:
        """Initialize database state."""
        self.tables: Dict[str, Type[Model]] = {}
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load database metadata."""
        meta_file = self.meta_path / "metadata.json"
        if meta_file.exists():
            with meta_file.open() as f:
                return json.load(f)
        return {"version": 1, "tables": {}}
    
    @contextmanager
    def transaction(self):
        """Start a new transaction."""
        transaction = self.transaction_manager.begin()
        try:
            yield transaction
            self.transaction_manager.commit(transaction)
        except Exception as e:
            self.transaction_manager.rollback(transaction)
            raise JsonDBError(f"Transaction failed: {str(e)}")
    
    def add(self, model: Model) -> None:
        """Add a model instance to the database."""
        table = model.__class__.__name__
        if table not in self.tables:
            self.tables[table] = type(model)
        
        data = model.dict()
        self.chunk_manager.add_record(table, data)
        self.index_manager.update_indexes(table, data)
    
    def bulk_insert(self, model_class: Type[T], records: List[Dict]) -> None:
        """Bulk insert records."""
        with self.transaction() as transaction:
            for record in records:
                instance = model_class(**record)
                self.add(instance)
                transaction.add_operation({
                    "type": "insert",
                    "table": model_class.__name__,
                    "data": record
                })
    
    def query(self, model_class: Type[T]) -> "QueryBuilder":
        """Create a new query builder for the model."""
        from .query import QueryBuilder
        return QueryBuilder(self, model_class)
    
    def migrate_to_sqlmodel(self, engine) -> None:
        """Migrate database to SQLModel."""
        from sqlmodel import SQLModel
        
        # Create tables
        SQLModel.metadata.create_all(engine)
        
        # Migrate data
        for table_name, model_class in self.tables.items():
            records = self.query(model_class).all()
            with engine.begin() as conn:
                for record in records:
                    stmt = model_class.__table__.insert().values(**record.dict())
                    conn.execute(stmt)
