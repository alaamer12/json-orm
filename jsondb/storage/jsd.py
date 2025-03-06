"""JSD (JSON Database) file format implementation."""

import os
from multiprocessing import shared_memory
from pathlib import Path
from typing import Any, Dict, Optional, Union

import numpy as np
import orjson
import xxhash


class JSDFile:
    """JSD file format handler."""
    
    # Size threshold for using memory mapping
    SHARED_MEM_THRESHOLD = 1024 * 1024  # 1MB
    
    def __init__(self, path: Union[str, Path]):
        """Initialize JSD file."""
        self.path = Path(path)
        self._data: Optional[Dict[str, Any]] = None
        self._shared_mem: Optional[shared_memory.SharedMemory] = None
        self._data_hash: Optional[str] = None
        self._mmap: Optional[np.memmap] = None
        
    def _get_data_hash(self, data: Dict[str, Any]) -> str:
        """Get fast hash of data for cache validation."""
        return xxhash.xxh64(orjson.dumps(data)).hexdigest()
    
    def write(self, data: Dict[str, Any]) -> None:
        """Write data to JSD file."""
        # Check if data changed
        new_hash = self._get_data_hash(data)
        if new_hash == self._data_hash:
            return
            
        # Cache data and hash
        self._data = data
        self._data_hash = new_hash
        
        # Convert to bytes
        json_bytes = orjson.dumps(
            data,
            option=orjson.OPT_SERIALIZE_NUMPY | 
                   orjson.OPT_SERIALIZE_DATACLASS |
                   orjson.OPT_PASSTHROUGH_DATACLASS
        )
        
        # For large data, use memory mapping
        if len(json_bytes) >= self.SHARED_MEM_THRESHOLD:
            # Create memory mapped array
            if self._mmap is not None:
                self._mmap.flush()
                del self._mmap
            
            # Create new memmap with exact size
            self._mmap = np.memmap(
                self.path, 
                dtype='uint8',
                mode='w+',
                shape=(len(json_bytes),)
            )
            # Write data
            self._mmap[:] = np.frombuffer(json_bytes, dtype='uint8')
            self._mmap.flush()
        else:
            # For small data, write directly
            with open(self.path, 'wb') as f:
                f.write(json_bytes)
            if self._mmap is not None:
                del self._mmap
                self._mmap = None
    
    def read(self) -> Dict[str, Any]:
        """Read data from JSD file."""
        # Return cached data if available
        if self._data is not None:
            return self._data
            
        file_size = os.path.getsize(self.path)
        
        # Use memory mapping for large files
        if file_size >= self.SHARED_MEM_THRESHOLD:
            # Create or reuse memory map
            if self._mmap is None:
                self._mmap = np.memmap(
                    self.path,
                    dtype='uint8',
                    mode='r',
                    shape=(file_size,)
                )
            # Convert to bytes and parse
            data = bytes(self._mmap)
        else:
            # Read directly for small files
            with open(self.path, 'rb') as f:
                data = f.read()
            if self._mmap is not None:
                del self._mmap
                self._mmap = None
        
        # Parse and cache
        self._data = orjson.loads(data)
        self._data_hash = xxhash.xxh64(data).hexdigest()
        return self._data
    
    def append(self, data: Dict[str, Any]) -> None:
        """Append data to existing JSD file."""
        # Use cached data if available
        if self._data is not None:
            if isinstance(self._data, dict):
                self._data.update(data)
                self.write(self._data)
                return
                
        # Otherwise read and update
        try:
            existing = self.read()
        except FileNotFoundError:
            existing = {}
            
        if isinstance(existing, dict):
            existing.update(data)
            self.write(existing)
        else:
            raise ValueError("Existing data is not a dictionary")
    
    def flush(self) -> None:
        """Flush cached data to disk."""
        if self._data is not None:
            self.write(self._data)
        if self._mmap is not None:
            self._mmap.flush()
    
    def clear_cache(self) -> None:
        """Clear cached data."""
        self._data = None
        self._data_hash = None
        if self._shared_mem:
            self._shared_mem.close()
            self._shared_mem.unlink()
            self._shared_mem = None
        if self._mmap is not None:
            self._mmap.flush()
            del self._mmap
            self._mmap = None
    
    @property
    def exists(self) -> bool:
        """Check if the file exists."""
        return self.path.exists()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear_cache()
