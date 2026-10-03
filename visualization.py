"""Visualization module for page-replacement experimental results.

Generates clean, student-friendly charts for:
1. Total page faults across frame sizes
2. Overall hit ratio across frame sizes
3. Hit ratio before vs. after workload shift (main frame size)
"""
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def generate_all_plots(df: pd.DataFrame, output_dir: str = "results", main_frames: int = 4) -> None:
    """Generates and saves the three report figures."""
    os.makedirs(output_dir, exist_ok=True)
    plot_page_faults(df, os.path.join(output_dir, "page_faults.png"))
    plot_hit_ratio(df, os.path.join(output_dir, "hit_ratio.png"))
    plot_before_after_shift(df, os.path.join(output_dir, "before_after_shift.png"), main_frames=main_frames)


def plot_page_faults(df: pd.DataFrame, save_path: str) -> None:
    """Plots total page faults across different frame allocations."""
    algorithms = ["FIFO", "LRU", "Optimal", "Learned"]
    frame_sizes = sorted(df["Frames"].unique())

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(frame_sizes))
    width = 0.18

    # Colors suitable for academic reports
    colors = ["#4e79a7", "#f28e2b", "#59a14f", "#e15759"]

    for i, algo in enumerate(algorithms):
        sub = df[df["Algorithm"] == algo].sort_values("Frames")
        faults = sub["Overall_Faults"].values
        offset = (i - 1.5) * width
        rects = ax.bar(x + offset, faults, width, label=algo, color=colors[i], edgecolor="black", linewidth=0.8)
        # Add value label above bar
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f"{int(height)}",
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha="center", va="bottom", fontsize=8)

    ax.set_xlabel("Number of Frames", fontsize=11, fontweight="bold")
    ax.set_ylabel("Total Page Faults", fontsize=11, fontweight="bold")
    ax.set_title("Total Page Faults by Algorithm and Frame Size", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{f} Frames" for f in frame_sizes])
    ax.legend(title="Algorithm", loc="upper right")
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    fig.tight_layout()
    fig.savefig(save_path, dpi=300)
    plt.close(fig)


def plot_hit_ratio(df: pd.DataFrame, save_path: str) -> None:
    """Plots overall hit ratio across different frame allocations."""
    algorithms = ["FIFO", "LRU", "Optimal", "Learned"]
    frame_sizes = sorted(df["Frames"].unique())

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(frame_sizes))
    width = 0.18
    colors = ["#4e79a7", "#f28e2b", "#59a14f", "#e15759"]

    for i, algo in enumerate(algorithms):
        sub = df[df["Algorithm"] == algo].sort_values("Frames")
        hit_ratios = [val * 100.0 for val in sub["Overall_Hit_Ratio"].values]
        offset = (i - 1.5) * width
        rects = ax.bar(x + offset, hit_ratios, width, label=algo, color=colors[i], edgecolor="black", linewidth=0.8)
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f"{height:.1f}%",
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha="center", va="bottom", fontsize=8)

    ax.set_xlabel("Number of Frames", fontsize=11, fontweight="bold")
    ax.set_ylabel("Overall Hit Ratio (%)", fontsize=11, fontweight="bold")
    ax.set_title("Overall Hit Ratio by Algorithm and Frame Size", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{f} Frames" for f in frame_sizes])
    ax.set_ylim(0, 100)
    ax.legend(title="Algorithm", loc="upper left")
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    fig.tight_layout()
    fig.savefig(save_path, dpi=300)
    plt.close(fig)


def plot_before_after_shift(df: pd.DataFrame, save_path: str, main_frames: int = 4) -> None:
    """Plots Phase 1 vs Phase 2 hit ratio to show the impact of the workload shift."""
    subset = df[df["Frames"] == main_frames].copy()
    algorithms = ["FIFO", "LRU", "Optimal", "Learned"]

    # Reorder according to algorithms list
    subset["Algorithm"] = pd.Categorical(subset["Algorithm"], categories=algorithms, ordered=True)
    subset = subset.sort_values("Algorithm")

    p1_hits = [row["P1_Hit_Ratio"] * 100.0 for _, row in subset.iterrows()]
    p2_hits = [row["P2_Hit_Ratio"] * 100.0 for _, row in subset.iterrows()]

    x = np.arange(len(algorithms))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    rects1 = ax.bar(x - width/2, p1_hits, width, label="Phase 1 (Locality-Heavy)",
                    color="#2b5c8f", edgecolor="black", linewidth=0.8)
    rects2 = ax.bar(x + width/2, p2_hits, width, label="Phase 2 (Random Access)",
                    color="#d95f02", edgecolor="black", linewidth=0.8)

    for rect in rects1:
        height = rect.get_height()
        ax.annotate(f"{height:.1f}%",
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8)

    for rect in rects2:
        height = rect.get_height()
        ax.annotate(f"{height:.1f}%",
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8)

    ax.set_xlabel("Page Replacement Algorithm", fontsize=11, fontweight="bold")
    ax.set_ylabel("Hit Ratio (%)", fontsize=11, fontweight="bold")
    ax.set_title(f"Impact of Workload Shift on Hit Ratio ({main_frames} Frames)", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(algorithms, fontsize=10)
    ax.set_ylim(0, 105)
    ax.legend(loc="upper right")
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    fig.tight_layout()
    fig.savefig(save_path, dpi=300)
    plt.close(fig)
