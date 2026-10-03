"""Algorithms package for page replacement."""
from algorithms.fifo import run_fifo
from algorithms.lru import run_lru
from algorithms.optimal import run_optimal
from algorithms.learned import run_learned

__all__ = ["run_fifo", "run_lru", "run_optimal", "run_learned"]
