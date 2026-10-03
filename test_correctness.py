"""Correctness and Invariant Testing for Page Replacement Algorithms.

Verifies:
1. Standard textbook benchmark results (Silberschatz et al., Operating System Concepts).
2. Edge cases (empty sequence, single frame, repeated page, frames > unique pages).
3. The fundamental invariant: Optimal page faults <= FIFO faults and <= LRU faults.
"""
import random
from algorithms.fifo import run_fifo
from algorithms.lru import run_lru
from algorithms.optimal import run_optimal


def test_textbook_example():
    """Verifies standard benchmark from Silberschatz et al. (3 frames)."""
    ref_str = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
    frames = 3

    fifo_res = run_fifo(ref_str, frames)
    lru_res = run_lru(ref_str, frames)
    opt_res = run_optimal(ref_str, frames)

    assert fifo_res["faults"] == 15, f"Expected FIFO faults=15, got {fifo_res['faults']}"
    assert lru_res["faults"] == 12, f"Expected LRU faults=12, got {lru_res['faults']}"
    assert opt_res["faults"] == 9, f"Expected Optimal faults=9, got {opt_res['faults']}"
    print("[PASS] Textbook benchmark passed (FIFO=15, LRU=12, Optimal=9).")


def test_edge_cases():
    """Verifies edge case handling across algorithms."""
    # 1. Empty reference sequence
    for algo, fn in [("FIFO", run_fifo), ("LRU", run_lru), ("Optimal", run_optimal)]:
        res = fn([], 3)
        assert res["total_references"] == 0
        assert res["faults"] == 0
        assert res["hits"] == 0
    print("[PASS] Edge Case 1: Empty reference sequence passed.")

    # 2. Repeated single page
    repeated = [5, 5, 5, 5, 5]
    for algo, fn in [("FIFO", run_fifo), ("LRU", run_lru), ("Optimal", run_optimal)]:
        res = fn(repeated, 3)
        assert res["faults"] == 1, f"{algo} expected 1 fault on repeated, got {res['faults']}"
        assert res["hits"] == 4, f"{algo} expected 4 hits on repeated, got {res['hits']}"
    print("[PASS] Edge Case 2: Repeated single page passed.")

    # 3. Frames larger than unique pages
    small_set = [1, 2, 3, 1, 2, 3, 1, 2, 3]
    for algo, fn in [("FIFO", run_fifo), ("LRU", run_lru), ("Optimal", run_optimal)]:
        res = fn(small_set, 10)
        assert res["faults"] == 3, f"{algo} expected 3 faults with large frame pool, got {res['faults']}"
        assert res["hits"] == 6, f"{algo} expected 6 hits with large frame pool, got {res['hits']}"
    print("[PASS] Edge Case 3: More frames than unique pages passed.")

    # 4. Single frame alternating
    alt = [1, 2, 1, 2]
    for algo, fn in [("FIFO", run_fifo), ("LRU", run_lru), ("Optimal", run_optimal)]:
        res = fn(alt, 1)
        assert res["faults"] == 4, f"{algo} expected 4 faults on 1 frame alternating, got {res['faults']}"
        assert res["hits"] == 0
    print("[PASS] Edge Case 4: Single frame alternating access passed.")


def test_optimal_invariance():
    """Verifies that Optimal never produces more page faults than FIFO or LRU."""
    rng = random.Random(999)
    for trial in range(10):
        length = rng.randint(50, 150)
        pages = [rng.randint(0, 12) for _ in range(length)]
        frames = rng.randint(2, 6)

        fifo_res = run_fifo(pages, frames)
        lru_res = run_lru(pages, frames)
        opt_res = run_optimal(pages, frames)

        assert opt_res["faults"] <= fifo_res["faults"], (
            f"Trial {trial}: Optimal ({opt_res['faults']}) worse than FIFO ({fifo_res['faults']})"
        )
        assert opt_res["faults"] <= lru_res["faults"], (
            f"Trial {trial}: Optimal ({opt_res['faults']}) worse than LRU ({lru_res['faults']})"
        )
    print("[PASS] Invariant: Optimal is consistently <= FIFO and LRU across random traces.")


def run_all_correctness_tests():
    """Runs all test suites."""
    print("=" * 60)
    print("RUNNING ALGORITHM CORRECTNESS & EDGE CASE TESTS")
    print("=" * 60)
    test_textbook_example()
    test_edge_cases()
    test_optimal_invariance()
    print("=" * 60)
    print("ALL CORRECTNESS TESTS PASSED SUCCESSFULLY!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_all_correctness_tests()
