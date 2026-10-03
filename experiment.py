"""Experiment runner for comparing page replacement algorithms across frame sizes and workload phases.
"""
from typing import List, Dict, Any
import pandas as pd

from algorithms.fifo import run_fifo
from algorithms.lru import run_lru
from algorithms.optimal import run_optimal
from algorithms.learned import run_learned


def run_single_comparison(
    test_trace: List[int],
    num_frames: int,
    model: Any,
    shift_point: int = 500
) -> List[Dict[str, Any]]:
    """Runs all 4 algorithms on the same test trace for a specific frame size."""
    algorithms = [
        ("FIFO", lambda: run_fifo(test_trace, num_frames, shift_point)),
        ("LRU", lambda: run_lru(test_trace, num_frames, shift_point)),
        ("Optimal", lambda: run_optimal(test_trace, num_frames, shift_point)),
        ("Learned", lambda: run_learned(test_trace, num_frames, model, shift_point)),
    ]

    records = []
    for name, runner in algorithms:
        res = runner()
        p1 = res["phase1"]
        p2 = res["phase2"]

        # Calculate absolute and percentage change across shift
        hit_drop = p1["hit_ratio"] - p2["hit_ratio"]
        pct_drop = (hit_drop / p1["hit_ratio"] * 100.0) if p1["hit_ratio"] > 0 else 0.0

        record = {
            "Algorithm": name,
            "Frames": num_frames,
            "Total_Refs": res["total_references"],
            "Overall_Hits": res["hits"],
            "Overall_Faults": res["faults"],
            "Overall_Hit_Ratio": round(res["hit_ratio"], 4),
            "Overall_Fault_Ratio": round(res["fault_ratio"], 4),
            "P1_Hits": p1["hits"],
            "P1_Faults": p1["faults"],
            "P1_Hit_Ratio": round(p1["hit_ratio"], 4),
            "P2_Hits": p2["hits"],
            "P2_Faults": p2["faults"],
            "P2_Hit_Ratio": round(p2["hit_ratio"], 4),
            "Hit_Ratio_Drop": round(hit_drop, 4),
            "Hit_Ratio_Drop_Pct": round(pct_drop, 2),
        }
        records.append(record)

    return records


def run_all_experiments(
    test_trace: List[int],
    model: Any,
    frame_sizes: List[int] = [3, 4, 5],
    shift_point: int = 500
) -> pd.DataFrame:
    """Runs the full experimental battery across multiple frame sizes.

    Returns:
        pd.DataFrame containing all experimental records.
    """
    all_records = []
    for f in frame_sizes:
        records = run_single_comparison(
            test_trace=test_trace,
            num_frames=f,
            model=model,
            shift_point=shift_point
        )
        all_records.extend(records)

    df = pd.DataFrame(all_records)
    return df


def format_summary_table(df: pd.DataFrame, frames: int = 4) -> str:
    """Formats a clean, student-friendly text table for console display."""
    subset = df[df["Frames"] == frames]
    header = (
        f"\n{'='*78}\n"
        f"DETAILED EXPERIMENT RESULTS (Frame Size = {frames})\n"
        f"{'='*78}\n"
        f"{'Algorithm':<10} | {'Phase 1 (Locality)':<18} | {'Phase 2 (Random)':<18} | {'Overall':<20}\n"
        f"{'':<10} | {'Hits / Faults (Hit%)':<18} | {'Hits / Faults (Hit%)':<18} | {'Hits / Faults (Hit%)':<20}\n"
        f"{'-'*78}"
    )
    lines = [header]
    for _, row in subset.iterrows():
        p1_str = f"{row['P1_Hits']}/{row['P1_Faults']} ({row['P1_Hit_Ratio']*100:.1f}%)"
        p2_str = f"{row['P2_Hits']}/{row['P2_Faults']} ({row['P2_Hit_Ratio']*100:.1f}%)"
        ov_str = f"{row['Overall_Hits']}/{row['Overall_Faults']} ({row['Overall_Hit_Ratio']*100:.1f}%)"
        line = f"{row['Algorithm']:<10} | {p1_str:<18} | {p2_str:<18} | {ov_str:<20}"
        lines.append(line)
    lines.append("="*78)
    return "\n".join(lines)
