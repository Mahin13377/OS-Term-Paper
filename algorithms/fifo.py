"""First-In First-Out (FIFO) Page Replacement Algorithm.

Evicts the page that has been in memory the longest (oldest arrival).
"""
from collections import deque
from typing import List, Dict, Any, Optional


def run_fifo(
    reference_sequence: List[int],
    num_frames: int,
    shift_point: Optional[int] = None
) -> Dict[str, Any]:
    """Simulates FIFO page replacement on a given reference sequence.

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
            "algorithm": "FIFO",
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

    resident_set = set()
    fifo_queue = deque()

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
                fifo_queue.append(page)
            else:
                oldest_page = fifo_queue.popleft()
                resident_set.remove(oldest_page)
                resident_set.add(page)
                fifo_queue.append(page)

    p1_refs = min(shift_point, total_refs)
    p2_refs = max(0, total_refs - p1_refs)

    return {
        "algorithm": "FIFO",
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
