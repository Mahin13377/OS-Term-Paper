"""Synthetic Workload Generator with Configurable Workload Shift.

Generates reproducible memory page reference sequences exhibiting two distinct phases:
- Phase 1: High temporal and spatial locality (small working set, sequential loops).
- Phase 2: Low locality / random access across a larger page address space.
"""
import random
import json
from typing import List, Tuple, Optional


def generate_workload(
    total_refs: int = 1000,
    shift_point: int = 500,
    p1_pages: Tuple[int, int] = (0, 6),   # [0, 5] working set
    p2_pages: Tuple[int, int] = (0, 20),  # [0, 19] page range
    seed: Optional[int] = 42
) -> List[int]:
    """Generates a synthetic page-reference trace with a clear workload shift.

    Args:
        total_refs: Total number of memory page references (default: 1000).
        shift_point: Reference index at which workload shifts to Phase 2 (default: 500).
        p1_pages: (min_page, max_page) range for Phase 1 working set.
        p2_pages: (min_page, max_page) range for Phase 2 page universe.
        seed: Random seed for exact reproducibility.

    Returns:
        List of integer page IDs.
    """
    rng = random.Random(seed)
    trace = []

    p1_min, p1_max = p1_pages
    p1_working_set = list(range(p1_min, p1_max))

    p2_min, p2_max = p2_pages
    p2_page_range = list(range(p2_min, p2_max))

    # Phase 1: High Locality (sequential scans, repeated accesses, tight loops)
    current_page = p1_working_set[0]
    for _ in range(shift_point):
        r = rng.random()
        if r < 0.40:
            # Sequential access (spatial locality)
            current_page = (current_page + 1) % len(p1_working_set)
        elif r < 0.75:
            # Re-reference recent page or loop back (temporal locality)
            current_page = rng.choice(p1_working_set[:3])
        else:
            # Minor fluctuation within small working set
            current_page = rng.choice(p1_working_set)
        trace.append(current_page)

    # Phase 2: Uniform random access across pages 0-19 (destroys cache locality)
    for _ in range(total_refs - shift_point):
        _ = rng.random()  # maintains identical RNG stream alignment
        page = rng.choice(p2_page_range)
        trace.append(page)

    return trace


def generate_training_workloads(
    num_traces: int = 3,
    total_refs: int = 1000,
    shift_point: int = 500,
    base_seed: int = 1000
) -> List[List[int]]:
    """Generates independent training workloads to prevent data leakage."""
    traces = []
    for i in range(num_traces):
        trace = generate_workload(
            total_refs=total_refs,
            shift_point=shift_point,
            seed=base_seed + i * 37
        )
        traces.append(trace)
    return traces


def save_workload(trace: List[int], filepath: str) -> None:
    """Saves a reference trace to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(trace, f)


def load_workload(filepath: str) -> List[int]:
    """Loads a reference trace from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
