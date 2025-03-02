from pathlib import Path
from typing import Dict, List, Any, Set
import json

class Index:
    def __init__(self, name: str, unique: bool = False):
        self.name = name
        self.unique = unique
        self.values: Dict[Any, List[int]] = {}  # value -> list of record IDs
    
    def add(self, value: Any, record_id: int) -> None:
        """Add a value to the index."""
        if value not in self.values:
            self.values[value] = []
        
        if self.unique and self.values[value]:
            raise ValueError(f"Duplicate value for unique index: {value}")
        
        self.values[value].append(record_id)
    
    def remove(self, value: Any, record_id: int) -> None:
        """Remove a value from the index."""
        if value in self.values:
            self.values[value].remove(record_id)
            if not self.values[value]:
                del self.values[value]
    
    def find(self, value: Any) -> List[int]:
        """Find record IDs for a value."""
        return self.values.get(value, [])
    
    def to_dict(self) -> Dict:
        """Convert index to dictionary for storage."""
        return {
            "name": self.name,
            "unique": self.unique,
            "values": {
                str(k): v for k, v in self.values.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Index":
        """Create index from dictionary."""
        index = cls(data["name"], data["unique"])
        index.values = {
            eval(k): v for k, v in data["values"].items()
        }
        return index

class IndexManager:
    def __init__(self, index_path: Path):
        self.index_path = index_path
        self.indexes: Dict[str, Dict[str, Index]] = {}  # table -> field -> Index
    
    def ensure_index(self, table: str, field: str, unique: bool = False) -> None:
        """Ensure an index exists for a field."""
        if table not in self.indexes:
            self.indexes[table] = {}
        
        if field not in self.indexes[table]:
            self.indexes[table][field] = Index(field, unique)
            self._save_index(table, field)
    
    def update_indexes(self, table: str, record: Dict) -> None:
        """Update indexes for a record."""
        if table not in self.indexes:
            return
        
        record_id = record.get("id")
        if record_id is None:
            return
        
        for field, index in self.indexes[table].items():
            if field in record:
                index.add(record[field], record_id)
                self._save_index(table, field)
    
    def remove_from_indexes(self, table: str, record: Dict) -> None:
        """Remove record from indexes."""
        if table not in self.indexes:
            return
        
        record_id = record.get("id")
        if record_id is None:
            return
        
        for field, index in self.indexes[table].items():
            if field in record:
                index.remove(record[field], record_id)
                self._save_index(table, field)
    
    def find_by_index(self, table: str, field: str, value: Any) -> List[int]:
        """Find record IDs using an index."""
        if table not in self.indexes or field not in self.indexes[table]:
            return []
        
        return self.indexes[table][field].find(value)
    
    def _save_index(self, table: str, field: str) -> None:
        """Save index to disk."""
        index_file = self.index_path / table / f"{field}.json"
        index_file.parent.mkdir(parents=True, exist_ok=True)
        
        with index_file.open('w') as f:
            json.dump(self.indexes[table][field].to_dict(), f)
    
    def _load_index(self, table: str, field: str) -> None:
        """Load index from disk."""
        index_file = self.index_path / table / f"{field}.json"
        if not index_file.exists():
            return
        
        with index_file.open() as f:
            data = json.load(f)
            if table not in self.indexes:
                self.indexes[table] = {}
            self.indexes[table][field] = Index.from_dict(data)
