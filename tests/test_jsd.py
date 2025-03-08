"""Tests for JSD file format."""

import os
from pathlib import Path

import pytest

from json-orm.storage import JSDFile, JSDError


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file path."""
    return tmp_path / "test.jsd"


def test_write_read_basic(temp_file):
    """Test basic write and read operations."""
    data = {"name": "test", "value": 42}
    jsd = JSDFile(temp_file)
    jsd.write(data)
    
    assert jsd.exists
    read_data = jsd.read()
    assert read_data == data


def test_write_read_complex(temp_file):
    """Test with more complex data structures."""
    data = {
        "string": "hello",
        "integer": 42,
        "float": 3.14,
        "list": [1, 2, 3],
        "nested": {"a": 1, "b": 2},
        "null": None,
        "boolean": True
    }
    jsd = JSDFile(temp_file)
    jsd.write(data)
    
    read_data = jsd.read()
    assert read_data == data


def test_append(temp_file):
    """Test append operation."""
    initial_data = {"a": 1}
    append_data = {"b": 2}
    
    jsd = JSDFile(temp_file)
    jsd.write(initial_data)
    jsd.append(append_data)
    
    read_data = jsd.read()
    assert read_data == {"a": 1, "b": 2}


def test_compression(temp_file):
    """Test that compression reduces file size."""
    # Create a highly compressible dataset
    data = {"data": "test" * 1000}
    
    # Write without compression
    jsd_uncompressed = JSDFile(temp_file)
    jsd_uncompressed.write(data, compress=False)
    uncompressed_size = os.path.getsize(temp_file)
    
    # Write with compression
    jsd_compressed = JSDFile(temp_file)
    jsd_compressed.write(data, compress=True)
    compressed_size = os.path.getsize(temp_file)
    
    assert compressed_size < uncompressed_size


def test_invalid_file(temp_file):
    """Test reading an invalid file."""
    # Create an invalid file
    temp_file.write_bytes(b"Not a valid JSD file")
    
    jsd = JSDFile(temp_file)
    with pytest.raises(JSDError):
        jsd.read()


def test_header_info(temp_file):
    """Test header information."""
    data = {"test": "value"}
    jsd = JSDFile(temp_file)
    jsd.write(data)
    
    header = jsd.get_header()
    assert header is not None
    assert header.records == 1  # One key-value pair
    assert header.data_size > 0
