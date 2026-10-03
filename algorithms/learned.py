"""Learned / Adaptive Page Replacement Algorithm.

Uses a lightweight scikit-learn DecisionTreeClassifier trained on Optimal/Belady oracle labels.
For each resident page candidate, simple features (recency, frequency, age) are evaluated.
The candidate with the highest predicted eviction probability is evicted.
If scores are tied or uninformative, it falls back safely to LRU.
"""
from typing import List, Dict, Any, Optional, Set
import numpy as np


def extract_page_features(
    page: int,
    current_idx: int,
    last_used: Dict[int, int],
    arrival_time: Dict[int, int],
    reference_sequence: List[int],
    window_size: int = 50
) -> List[float]:
    """Extracts lightweight, explainable features for a candidate resident page.

    Features:
        1. recency: number of memory accesses since the page was last used.
        2. frequency: count of appearances of this page within a recent reference window.
        3. age: number of memory accesses since this page arrived in memory.
    """
    recency = float(current_idx - last_used.get(page, current_idx))
    age = float(current_idx - arrival_time.get(page, current_idx))

    window_start = max(0, current_idx - window_size)
    window = reference_sequence[window_start:current_idx]
    frequency = float(window.count(page))

    return [recency, frequency, age]


def select_learned_victim(
    resident_set: Set[int],
    current_idx: int,
    last_used: Dict[int, int],
    arrival_time: Dict[int, int],
    reference_sequence: List[int],
    model: Any,
    window_size: int = 50
) -> int:
    """Selects the victim page to evict using the learned model.

    Evaluates eviction probability for each resident page.
    Falls back to LRU (highest recency) when probabilities are tied.
    """
    candidate_list = list(resident_set)
    feature_matrix = []

    for page in candidate_list:
        feats = extract_page_features(
            page=page,
            current_idx=current_idx,
            last_used=last_used,
            arrival_time=arrival_time,
            reference_sequence=reference_sequence,
            window_size=window_size
        )
        feature_matrix.append(feats)

    # If model is not available, default to LRU
    if model is None:
        return max(candidate_list, key=lambda p: current_idx - last_used[p])

    try:
        # Check if model has predict_proba
        probs = model.predict_proba(feature_matrix)
        # Class 1 corresponds to "evict"
        classes = list(model.classes_)
        if 1 in classes:
            evict_col = classes.index(1)
            eviction_scores = probs[:, evict_col]
        else:
            # Model only observed class 0
            eviction_scores = np.zeros(len(candidate_list))
    except Exception:
        # Fallback if prediction fails
        return max(candidate_list, key=lambda p: current_idx - last_used[p])

    # Find candidate(s) with maximum eviction score
    max_score = np.max(eviction_scores)
    # Get all indices with max_score (within small floating point epsilon)
    best_candidates = [
        candidate_list[i]
        for i, score in enumerate(eviction_scores)
        if abs(score - max_score) < 1e-6
    ]

    # If tie, use LRU as safe fallback
    if len(best_candidates) == 1:
        return best_candidates[0]
    else:
        return max(best_candidates, key=lambda p: current_idx - last_used[p])


def run_learned(
    reference_sequence: List[int],
    num_frames: int,
    model: Any,
    shift_point: Optional[int] = None,
    window_size: int = 50
) -> Dict[str, Any]:
    """Simulates Learned page replacement using a trained decision tree model.

    Args:
        reference_sequence: Sequence of referenced page numbers.
        num_frames: Number of available physical memory frames.
        model: Trained DecisionTreeClassifier.
        shift_point: Index where workload shifts from Phase 1 to Phase 2.
        window_size: Recent access window length for frequency calculation.

    Returns:
        Dictionary containing overall and phase-specific statistics.
    """
    total_refs = len(reference_sequence)
    if total_refs == 0 or num_frames <= 0:
        return {
            "algorithm": "Learned",
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
    last_used = {}
    arrival_time = {}

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
            last_used[page] = idx
        else:
            faults += 1
            if is_p1:
                p1_faults += 1
            else:
                p2_faults += 1

            if len(resident_set) < num_frames:
                resident_set.add(page)
                last_used[page] = idx
                arrival_time[page] = idx
            else:
                victim = select_learned_victim(
                    resident_set=resident_set,
                    current_idx=idx,
                    last_used=last_used,
                    arrival_time=arrival_time,
                    reference_sequence=reference_sequence,
                    model=model,
                    window_size=window_size
                )
                resident_set.remove(victim)
                last_used.pop(victim, None)
                arrival_time.pop(victim, None)

                resident_set.add(page)
                last_used[page] = idx
                arrival_time[page] = idx

    p1_refs = min(shift_point, total_refs)
    p2_refs = max(0, total_refs - p1_refs)

    return {
        "algorithm": "Learned",
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
