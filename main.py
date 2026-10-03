"""Main entry point for CSE-307 Operating Systems Term Paper Project:
'Learning-Augmented Page Replacement: Classical Algorithms Under Workload Shift'

Executes the complete experimental pipeline:
1. Validates classical algorithm correctness against textbook benchmarks and invariants.
2. Generates independent training workloads and trains the Decision Tree oracle model.
3. Generates the testing workload with a prominent shift at index 500.
4. Evaluates FIFO, LRU, Optimal, and Learned policies across multiple frame sizes.
5. Displays comprehensive before/after shift comparative statistics in the console.
6. Saves detailed data to results/results.csv and outputs visualization plots.
"""
import os
import sys

from test_correctness import run_all_correctness_tests
from train_model import train_replacement_model
from workload import generate_workload, save_workload
from experiment import run_all_experiments, format_summary_table
from visualization import generate_all_plots


def main():
    print("=" * 78)
    print("CSE-307: OPERATING SYSTEMS INDIVIDUAL TERM-PAPER PROJECT")
    print("Title: Learning-Augmented Page Replacement: Classical Algorithms Under Workload Shift")
    print("=" * 78)

    # 1. Run correctness checks
    run_all_correctness_tests()

    # 2. Train Learned Replacement Model
    print("[STEP 1/5] Generating training workloads and training Decision Tree oracle model...")
    model, metadata = train_replacement_model(
        num_traces=4,
        refs_per_trace=1000,
        num_frames=4,
        window_size=50,
        seed=100
    )
    print(f" -> Training traces: {metadata['num_training_traces']} (1000 refs each)")
    print(f" -> Total candidate samples: {metadata['total_samples']}")
    print(f" -> Tree depth: {metadata['max_depth']}, Leaves: {metadata['n_leaves']}")
    print(" -> Feature Importances:")
    for feat, imp in metadata["feature_importances"].items():
        print(f"    - {feat:<12}: {imp:.4f}")
    print()

    # 3. Generate Testing Workload with Shift
    total_refs = 1000
    shift_point = 500
    test_seed = 42

    print(f"[STEP 2/5] Generating independent testing trace ({total_refs} total references)...")
    print(f" -> Phase 1 (0 to {shift_point - 1}): Locality-heavy sequential/looping accesses on pages [0..5]")
    print(f" >>> [WORKLOAD SHIFT OCCURS AT REFERENCE {shift_point}] <<<")
    print(f" -> Phase 2 ({shift_point} to {total_refs - 1}): Uniform random access across pages 0-19")

    test_trace = generate_workload(
        total_refs=total_refs,
        shift_point=shift_point,
        p1_pages=(0, 6),
        p2_pages=(0, 20),
        seed=test_seed
    )

    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    trace_file = os.path.join(results_dir, "test_trace.json")
    save_workload(test_trace, trace_file)
    print(f" -> Saved testing trace to '{trace_file}'.\n")

    # 4. Run Experiments
    frame_sizes = [3, 4, 5]
    print(f"[STEP 3/5] Running FIFO, LRU, Optimal, and Learned on identical test trace across frame sizes {frame_sizes}...")
    df_results = run_all_experiments(
        test_trace=test_trace,
        model=model,
        frame_sizes=frame_sizes,
        shift_point=shift_point
    )

    # 5. Display Console Results
    print(format_summary_table(df_results, frames=4))

    print("\nSummary Across All Frame Sizes (Overall Hit Ratio %):")
    pivot_hits = df_results.pivot(index="Algorithm", columns="Frames", values="Overall_Hit_Ratio") * 100.0
    print(pivot_hits.round(2).to_string())

    print("\nSummary Across All Frame Sizes (Total Page Faults):")
    pivot_faults = df_results.pivot(index="Algorithm", columns="Frames", values="Overall_Faults")
    print(pivot_faults.to_string())

    # 6. Save CSV
    csv_path = os.path.join(results_dir, "results.csv")
    df_results.to_csv(csv_path, index=False)
    print(f"\n[STEP 4/5] Saved complete experimental data to '{csv_path}'.")

    # 7. Generate Visualizations
    print("[STEP 5/5] Generating publication-quality charts...")
    generate_all_plots(df_results, output_dir=results_dir, main_frames=4)
    print(f" -> Generated '{os.path.join(results_dir, 'page_faults.png')}'")
    print(f" -> Generated '{os.path.join(results_dir, 'hit_ratio.png')}'")
    print(f" -> Generated '{os.path.join(results_dir, 'before_after_shift.png')}'")

    print("\n" + "=" * 78)
    print("EXPERIMENT EXECUTION COMPLETED SUCCESSFULLY!")
    print("=" * 78)


if __name__ == "__main__":
    main()
