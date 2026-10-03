"""Optimal (Belady's Min) Page Replacement Algorithm.

Evicts the page that will not be used for the longest period of time in the future.
Acts as the theoretical upper bound (oracle) for page replacement performance.
"""
from typing import List, Dict, Any, Optional, Set
import bisect


def find_optimal_victim(
    resident_set: Set[int],
    reference_sequence: List[int],
    current_idx: int,
    page_future_indices: Optional[Dict[int, List[int]]] = None
) -> int:
    """Finds the page in resident_set that will not be used for the longest period.

    Args:
        resident_set: Set of page numbers currently in memory frames.
        reference_sequence: Full reference sequence.
        current_idx: Current reference index.
        page_future_indices: Optional precomputed dict mapping page -> list of indices.

    Returns:
        The page number selected for eviction.
    """
    furthest_page = None
    max_distance = -1

    for page in resident_set:
        if page_future_indices is not None and page in page_future_indices:
            # Use binary search to find next access index > current_idx
            idx_list = page_future_indices[page]
            pos = bisect.bisect_right(idx_list, current_idx)
            if pos < len(idx_list):
                next_use = idx_list[pos]
            else:
                next_use = float('inf')
        else:
            # Linear scan forward fallback
            try:
                next_use = reference_sequence.index(page, current_idx + 1)
            except ValueError:
                next_use = float('inf')

        if next_use > max_distance:
            max_distance = next_use
            furthest_page = page

    return furthest_page if furthest_page is not None else next(iter(resident_set))


def run_optimal(
    reference_sequence: List[int],
    num_frames: int,
    shift_point: Optional[int] = None
) -> Dict[str, Any]:
    """Simulates Optimal page replacement on a given reference sequence.

    Args:
        reference_sequence: Sequence of referenced page numbers.
        num_frames: Number of available physical memory frames.
        shift_point: Index where workload shifts from Phase 1 to Phase 2.

    Returns:
        Dictionary containing overall and phase-specific statistics.
    """
    total_refs = len(reference_sequence)
    if total_refs == 0 or num_frames <= 0:
        return {
            "algorithm": "Optimal",
            "num_frames": num_frames,
            "total_references": total_refs,
            "hits": 0,
            "faults": 0,
            "hit_ratio": 0.0,
            "fault_ratio": 0.0,
            "phase1": {"references": 0, "hits": 0, "faults": 0, "hit_ratio": 0.0, "fault_ratio": 0.0},
            "phase2": {"references": 0, "hits": 0, "faults": 0, "hit_ratio": 0.0, "fault_ratio": 0.0},
        }

    if shift_point is None:
        shift_point = total_refs // 2

    # Precompute occurrence indices for each page for fast lookup
    page_indices = {}
    for idx, page in enumerate(reference_sequence):
        if page not in page_indices:
            page_indices[page] = []
        page_indices[page].append(idx)

    resident_set = set()

    hits = 0
    faults = 0
    p1_hits = 0
    p1_faults = 0
    p2_hits = 0
    p2_faults = 0

    for idx, page in enumerate(reference_sequence):
        is_p1 = (idx < shift_point)

        if page in resident_set:
            hits += 1
            if is_p1:
                p1_hits += 1
            else:
                p2_hits += 1
        else:
            faults += 1
            if is_p1:
                p1_faults += 1
            else:
                p2_faults += 1

            if len(resident_set) < num_frames:
                resident_set.add(page)
            else:
                victim = find_optimal_victim(resident_set, reference_sequence, idx, page_indices)
                resident_set.remove(victim)
                resident_set.add(page)

    p1_refs = min(shift_point, total_refs)
    p2_refs = max(0, total_refs - p1_refs)

    return {
        "algorithm": "Optimal",
        "num_frames": num_frames,
        "total_references": total_refs,
        "hits": hits,
        "faults": faults,
        "hit_ratio": hits / total_refs,
        "fault_ratio": faults / total_refs,
        "phase1": {
            "references": p1_refs,
            "hits": p1_hits,
            "faults": p1_faults,
            "hit_ratio": (p1_hits / p1_refs) if p1_refs > 0 else 0.0,
            "fault_ratio": (p1_faults / p1_refs) if p1_refs > 0 else 0.0,
        },
        "phase2": {
            "references": p2_refs,
            "hits": p2_hits,
            "faults": p2_faults,
            "hit_ratio": (p2_hits / p2_refs) if p2_refs > 0 else 0.0,
            "fault_ratio": (p2_faults / p2_refs) if p2_refs > 0 else 0.0,
        },
    }
