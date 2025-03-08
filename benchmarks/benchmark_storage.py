"""Benchmark comparing JSD format with plain orjson."""

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import orjson
from faker import Faker
from tqdm.auto import tqdm

from json-orm.storage import JSDFile

fake = Faker()


def generate_test_data(num_records: int, include_numpy: bool = True) -> Dict[str, Any]:
    """Generate test data using Faker."""
    data = {
        "metadata": {
            "count": num_records,
            "version": "1.0",
            "timestamp": fake.iso8601()
        },
        "users": []
    }
    
    if include_numpy:
        data["arrays"] = {
            "float": np.random.rand(100).tolist(),
            "int": np.random.randint(0, 100, 100).tolist()
        }
    
    for i in tqdm(range(num_records), desc="Generating data", leave=False):
        data["users"].append({
            "id": i,
            "username": fake.user_name(),
            "email": fake.email(),
            "age": fake.random_int(18, 90),
            "active": fake.boolean()
        })
    
    return data


def benchmark_operation(func, *args, **kwargs) -> Tuple[float, Any]:
    """Benchmark a function call."""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    duration = time.perf_counter() - start
    return duration, result


def format_size(size: int) -> str:
    """Format size in bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


def run_benchmarks(sizes: List[int], iterations: int = 5):
    """Run benchmarks with different data sizes."""
    print(f"\nRunning Storage Format Benchmarks (averaged over {iterations} iterations)")
    print("=" * 100)
    print(f"{'Records':<10} {'Operation':<10} {'JSD':<15} {'orjson':<15} {'Diff':<15} {'JSD Size':<15} {'JSON Size':<15}")
    print("-" * 100)
    
    # Pre-create JSD file for fair comparison
    jsd = JSDFile(Path("benchmark_output/test.jsd"))
    json_path = Path("benchmark_output/test.json")
    
    for num_records in tqdm(sizes, desc="Testing different sizes"):
        jsd_write_times = []
        json_write_times = []
        jsd_read_times = []
        json_read_times = []
        json_data = None
        
        for i in tqdm(range(iterations), desc=f"Running {num_records} records", leave=False):
            # Generate fresh test data for each iteration
            data = generate_test_data(num_records)
            
            # Benchmark JSD write
            write_time, _ = benchmark_operation(jsd.write, data)
            jsd_write_times.append(write_time)
            
            # Benchmark orjson write (to file for fair comparison)
            write_time, json_data = benchmark_operation(orjson.dumps, data)
            json_write_times.append(write_time)
            # Write JSON to file to measure size
            with open(json_path, 'wb') as f:
                f.write(json_data)
            
            # Clear cache for fair read comparison if not last iteration
            if i < iterations - 1:
                jsd.clear_cache()
            
            # Benchmark JSD read
            read_time, _ = benchmark_operation(jsd.read)
            jsd_read_times.append(read_time)
            
            # Benchmark orjson read
            read_time, _ = benchmark_operation(orjson.loads, json_data)
            json_read_times.append(read_time)
        
        # Calculate averages
        jsd_write_avg = sum(jsd_write_times) / iterations * 1000  # to ms
        json_write_avg = sum(json_write_times) / iterations * 1000
        jsd_read_avg = sum(jsd_read_times) / iterations * 1000
        json_read_avg = sum(json_read_times) / iterations * 1000
        
        # Calculate sizes
        jsd_size = os.path.getsize("benchmark_output/test.jsd")
        json_size = os.path.getsize("benchmark_output/test.json")
        
        # Print results
        write_diff = ((jsd_write_avg - json_write_avg) / json_write_avg * 100)
        read_diff = ((jsd_read_avg - json_read_avg) / json_read_avg * 100)
        
        print(f"{num_records:<10} {'Write':<10} "
              f"{jsd_write_avg:>6.2f}ms     {json_write_avg:>6.2f}ms     "
              f"{write_diff:>6.2f}%     "
              f"{format_size(jsd_size):<15} {format_size(json_size):<15}")
        
        print(f"{'':<10} {'Read':<10} "
              f"{jsd_read_avg:>6.2f}ms     {json_read_avg:>6.2f}ms     "
              f"{read_diff:>6.2f}%")
        
        print("-" * 100)
    
    # Cleanup
    jsd.clear_cache()
    if json_path.exists():
        json_path.unlink()


if __name__ == "__main__":
    os.makedirs("benchmark_output", exist_ok=True)
    BENCHMARK_SIZES = [100, 1000, 10000, 100000]
    run_benchmarks(BENCHMARK_SIZES)
