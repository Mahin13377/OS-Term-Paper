# Learning-Augmented Page Replacement: Classical Algorithms Under Workload Shift

## 1. Project Overview & Objective

In virtual memory operating systems, page-replacement algorithms dictate which physical memory page to evict when a page fault occurs and all memory frames are occupied. While classical heuristics such as **FIFO** and **LRU** are widely studied under stable conditions, real-world execution frequently transitions across phases—such as shifting from tight computational loops to random memory accesses.

The objective of this project is to:
1. Implement and verify classical page replacement algorithms: **FIFO**, **LRU**, and **Optimal (Belady's Min)**.
2. Develop a lightweight, explainable **Learned / Adaptive Page-Replacement Policy** using a scikit-learn `DecisionTreeClassifier` trained with Optimal as an oracle.
3. Systematically evaluate algorithm performance under an abrupt **Workload Shift** (Phase 1: High Locality -> Phase 2: Uniform Random Access across pages 0–19).
4. Analyze how hit ratios and page faults change across different frame allocations (3, 4, and 5 frames).

---

## 2. Algorithms Implemented

| Algorithm | Description | Policy Principle |
| :--- | :--- | :--- |
| **FIFO** | First-In, First-Out | Evicts the page that entered physical memory earliest. |
| **LRU** | Least Recently Used | Evicts the page that has remained unreferenced for the longest time. |
| **Optimal** | Belady's Min Algorithm | Evicts the resident page whose next use is farthest in the future (theoretical upper bound / oracle). |
| **Learned** | Decision Tree Classifier | Evaluates `[recency, frequency, age]` for each resident page and predicts eviction probability; safely falls back to LRU. |

---

## 3. The Learned Component

Unlike black-box deep neural networks, our learning-augmented policy is intentionally lightweight, fast, and explainable:
- **Features per candidate page**:
  - `recency`: Accesses elapsed since the page was last referenced.
  - `frequency`: Appearances of the page in a recent sliding window of length 50.
  - `age`: Accesses elapsed since the page was loaded into its frame.
- **Oracle Supervision**:
  - When Optimal runs on independent training traces and encounters a page fault with full frames, it selects the optimal victim page.
  - Each resident page candidate is logged as an observation with label y = 1 if Optimal chose it for eviction, and y = 0 otherwise.
- **Online Replacement**:
  - At runtime, resident candidate pages are evaluated by the decision tree, and the page with the highest predicted eviction score is evicted. If scores are tied, it defaults to LRU.

---

## 4. Workload-Shift Experiment

The benchmark uses a synthetic memory reference trace of 1,000 accesses with a fixed seed (`seed=42`):
- **Phase 1 (Refs 0–499)**: Locality-heavy sequential and looping accesses within a small working set of pages [0..5].
- **Workload Shift (Ref 500)**: Abrupt transition to uncorrelated memory lookups.
- **Phase 2 (Refs 500–999)**: Uniform random access across pages 0–19, sharply degrading temporal and spatial locality.

---

## 5. Folder Structure

```
project/
│
├── main.py                 # Main entry point orchestrating tests, training, & experiments
├── test_correctness.py     # Textbook benchmarks & invariant checks (Silberschatz et al.)
├── workload.py             # Reproducible two-phase synthetic trace generator
├── train_model.py          # Oracle data extraction & DecisionTree training
├── experiment.py           # Experiment runner across frame sizes and phases
├── visualization.py        # Generates clean, publication-ready figures
├── requirements.txt        # Cross-platform dependencies
├── README.md               # Complete project documentation
├── .gitignore              # Git ignore rules (.venv, __pycache__, *.pyc)
│
├── algorithms/             # Modular, clean algorithm implementations
│   ├── __init__.py
│   ├── fifo.py             # First-In First-Out page replacement
│   ├── lru.py              # Least Recently Used page replacement
│   ├── optimal.py          # Belady's Optimal replacement algorithm
│   └── learned.py          # Learned Decision Tree policy with LRU fallback
│
├── results/                # Generated experimental outputs
│   ├── results.csv         # Measured empirical metrics across frame sizes & phases
│   ├── test_trace.json     # Saved 1,000-reference benchmark trace
│   ├── page_faults.png     # Total page faults bar chart across 3, 4, 5 frames
│   ├── hit_ratio.png       # Hit ratio comparison chart
│   └── before_after_shift.png # Phase 1 vs. Phase 2 hit ratio comparison (4 frames)
│
└── report/
    ├── CSE307_Term_Paper_202414064.docx # Formatted term paper report (Word)
    └── report.md                       # Term paper markdown source
```

---

## 6. Installation & Execution

The codebase is written in standard cross-platform Python 3 without any platform-specific file paths or APIs. It runs identically on Windows, Linux Ubuntu, and WSL.

### Option A: Windows (PowerShell)

```powershell
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate virtual environment
.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run correctness tests and full experiment
python main.py
```

### Option B: Linux Ubuntu / WSL

```bash
# 1. Create a virtual environment
python3 -m venv .venv

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run correctness tests and full experiment
python3 main.py
```

---

## 7. Expected Output

When running `python main.py`, the program will:
1. Validate all algorithms against the standard Silberschatz textbook reference string (`FIFO=15`, `LRU=12`, `Optimal=9` faults on 3 frames) and verify edge cases.
2. Train the Decision Tree on independent training traces and print feature importances.
3. Announce the exact point of the workload shift (`Reference 500`).
4. Display a comparison table for the baseline 4-frame setup and summary tables across 3, 4, and 5 frames.
5. Save `results/results.csv` and generate the three charts in `results/`.

---

## 8. Summary of Results (Baseline: 4 Frames)

Below are the actual numbers measured on the 1,000-reference test trace:

| Algorithm | Phase 1 Hit Ratio (Locality) | Phase 2 Hit Ratio (Random) | Overall Hit Ratio | Total Page Faults | Hit Ratio Decline across Shift |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **FIFO** | 63.60% | 20.00% | 41.80% | 582 | -43.60% (68.55% drop) |
| **LRU** | 67.40% | 20.00% | 43.70% | 563 | -47.40% (70.33% drop) |
| **Optimal** | 81.60% | 43.60% | 62.60% | 374 | -38.00% (46.57% drop) |
| **Learned** | 66.00% | 20.00% | 43.00% | 570 | -46.00% (69.70% drop) |

### Key Observations:
- **Under 3 frames (tight memory)**: In this experiment, the learned policy produced fewer faults than LRU with three frames (662 faults vs. 693 for LRU and 705 for FIFO). One possible reason is that the model considered age and frequency in addition to recency.
- **Under 4 and 5 frames**: Learned closely tracked LRU (43.0% vs. 43.7% for 4 frames; 54.0% vs. 54.5% for 5 frames).
- **Post-shift convergence**: In Phase 2, all online heuristics converged to exactly 20.00% hit ratio (4 frames / 20 pages), confirming that under uniform random access across pages 0–19, past access history provides zero predictive advantage.

---

## 9. Limitations

1. **Kernel Overhead**: Software execution of decision tree inference and sliding window frequency extraction adds latency not present in hardware clock-based LRU approximations.
2. **Feature Simplicity**: Does not include dirty/clean page states (disk write penalty) or variable memory access latency.
3. **Trace Domain Adaptation**: If testing access patterns diverge drastically from the training distribution, tree confidence drops and the policy relies on its fallback rule.

---

## 10. AI Assistance Disclosure

An AI coding assistant was used to assist with project scaffolding, debugging, and code formatting, in compliance with course guidelines. All experiments, simulations, and analyses were conducted and verified by the student.
