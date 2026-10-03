"""Training module for the Learning-Augmented Page Replacement Policy.

Uses the Optimal (Belady) algorithm as an oracle on separate training traces.
Extracts (recency, frequency, age) features and trains a DecisionTreeClassifier.
"""
from typing import List, Tuple, Any, Dict
import numpy as np
from sklearn.tree import DecisionTreeClassifier

from algorithms.optimal import find_optimal_victim
from algorithms.learned import extract_page_features
from workload import generate_training_workloads


def build_training_dataset(
    training_traces: List[List[int]],
    num_frames: int = 4,
    window_size: int = 50
) -> Tuple[np.ndarray, np.ndarray]:
    """Generates training data (X, y) by simulating Optimal replacement on training traces.

    For every eviction decision:
    - Each resident candidate page produces one sample.
    - Features: [recency, frequency, age].
    - Label: 1 if selected by Optimal for eviction, 0 otherwise.

    Returns:
        X: Feature matrix of shape (N, 3).
        y: Binary label vector of shape (N,).
    """
    X_list = []
    y_list = []

    for trace in training_traces:
        # Precompute page index occurrences for fast Optimal lookup
        page_indices = {}
        for idx, page in enumerate(trace):
            if page not in page_indices:
                page_indices[page] = []
            page_indices[page].append(idx)

        resident_set = set()
        last_used: Dict[int, int] = {}
        arrival_time: Dict[int, int] = {}

        for idx, page in enumerate(trace):
            if page in resident_set:
                last_used[page] = idx
            else:
                if len(resident_set) < num_frames:
                    resident_set.add(page)
                    last_used[page] = idx
                    arrival_time[page] = idx
                else:
                    # Identify the optimal victim
                    victim = find_optimal_victim(resident_set, trace, idx, page_indices)

                    # Create a training sample for each candidate currently in memory
                    for candidate in list(resident_set):
                        feats = extract_page_features(
                            page=candidate,
                            current_idx=idx,
                            last_used=last_used,
                            arrival_time=arrival_time,
                            reference_sequence=trace,
                            window_size=window_size
                        )
                        label = 1 if (candidate == victim) else 0
                        X_list.append(feats)
                        y_list.append(label)

                    # Update resident set following oracle choice
                    resident_set.remove(victim)
                    last_used.pop(victim, None)
                    arrival_time.pop(victim, None)

                    resident_set.add(page)
                    last_used[page] = idx
                    arrival_time[page] = idx

    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.int32)
    return X, y


def train_decision_tree(
    X: np.ndarray,
    y: np.ndarray,
    max_depth: int = 5,
    min_samples_split: int = 10,
    random_state: int = 42
) -> DecisionTreeClassifier:
    """Trains a simple, explainable DecisionTreeClassifier on eviction data."""
    clf = DecisionTreeClassifier(
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        random_state=random_state
    )
    clf.fit(X, y)
    return clf


def train_replacement_model(
    num_traces: int = 3,
    refs_per_trace: int = 1000,
    num_frames: int = 4,
    window_size: int = 50,
    seed: int = 100
) -> Tuple[DecisionTreeClassifier, Dict[str, Any]]:
    """End-to-end training pipeline for the learned page-replacement model.

    Generates independent training workloads, creates the feature dataset,
    and fits the DecisionTreeClassifier.

    Returns:
        model: Trained DecisionTreeClassifier.
        metadata: Dictionary with training statistics and feature importances.
    """
    training_traces = generate_training_workloads(
        num_traces=num_traces,
        total_refs=refs_per_trace,
        base_seed=seed
    )

    X, y = build_training_dataset(
        training_traces=training_traces,
        num_frames=num_frames,
        window_size=window_size
    )

    clf = train_decision_tree(X, y)

    feature_names = ["recency", "frequency", "age"]
    importances = dict(zip(feature_names, clf.feature_importances_))

    metadata = {
        "num_training_traces": len(training_traces),
        "total_samples": len(X),
        "positive_eviction_labels": int(np.sum(y == 1)),
        "negative_labels": int(np.sum(y == 0)),
        "max_depth": clf.get_depth(),
        "n_leaves": clf.get_n_leaves(),
        "feature_importances": importances,
    }

    return clf, metadata
