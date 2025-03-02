from pathlib import Path
from typing import Dict, List, Optional
import json
import shutil

class ChunkManager:
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size
        self.current_chunks: Dict[str, List[Dict]] = {}
        self.chunk_counts: Dict[str, int] = {}
    
    def get_chunk_path(self, table: str, chunk_id: int) -> Path:
        return Path(f"data/{table}/chunk_{chunk_id}.json")
    
    def add_record(self, table: str, record: Dict) -> None:
        """Add a record to the current chunk."""
        if table not in self.current_chunks:
            self.current_chunks[table] = []
            self.chunk_counts[table] = 0
        
        self.current_chunks[table].append(record)
        
        # If chunk is full, write to disk
        if len(self.current_chunks[table]) >= self.chunk_size:
            self._write_chunk(table)
    
    def _write_chunk(self, table: str) -> None:
        """Write current chunk to disk."""
        chunk_id = self.chunk_counts[table]
        chunk_path = self.get_chunk_path(table, chunk_id)
        
        # Ensure directory exists
        chunk_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write chunk
        with chunk_path.open('w') as f:
            json.dump(self.current_chunks[table], f)
        
        # Clear current chunk and increment counter
        self.current_chunks[table] = []
        self.chunk_counts[table] += 1
    
    def read_chunk(self, table: str, chunk_id: int) -> List[Dict]:
        """Read a chunk from disk."""
        chunk_path = self.get_chunk_path(table, chunk_id)
        if not chunk_path.exists():
            return []
        
        with chunk_path.open() as f:
            return json.load(f)
    
    def get_all_records(self, table: str) -> List[Dict]:
        """Get all records for a table."""
        records = []
        
        # Read all chunks
        for chunk_id in range(self.chunk_counts.get(table, 0)):
            records.extend(self.read_chunk(table, chunk_id))
        
        # Add records from current chunk
        if table in self.current_chunks:
            records.extend(self.current_chunks[table])
        
        return records
    
    def clear_table(self, table: str) -> None:
        """Clear all data for a table."""
        table_path = Path(f"data/{table}")
        if table_path.exists():
            shutil.rmtree(table_path)
        
        if table in self.current_chunks:
            del self.current_chunks[table]
            del self.chunk_counts[table]
