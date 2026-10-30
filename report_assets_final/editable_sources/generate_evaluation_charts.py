"""
Academic Evaluation Charts & Confusion Matrix Generator
SAFE-VISION (SafeAd AI) Trust and Safety Framework
Publication-quality Matplotlib heatmaps, bar charts, and profiling graphs
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Global style configuration
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#94A3B8'
plt.rcParams['axes.linewidth'] = 0.8

COLOR_NAVY = '#1E3A8A'
COLOR_BORDER_BLUE = '#3B82F6'
COLOR_TEAL = '#0F766E'
COLOR_AMBER = '#B45309'
COLOR_RED = '#B91C1C'
COLOR_SLATE = '#334155'
TEXT_DARK = '#0F172A'

CLASSES = ['SAFE_FOR_ALL', 'SAFE_14_PLUS', 'SAFE_18_PLUS', 'UNSAFE_FOR_ALL']
CLASSES_SHORT = ['SFA', 'S14P', 'S18P', 'UFA']

# Helper to plot a standard publication confusion matrix heatmap
def plot_academic_cm(cm, title, subtitle, out_png, out_svg, total_n, acc_val):
    fig, ax = plt.subplots(figsize=(7, 6.2), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')

    # Normalize by row (recall)
    cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    cm_norm = np.nan_to_num(cm_norm)

    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues, vmin=0, vmax=np.max(cm)*1.15)
    
    # Colorbar
    cbar = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=8)
    cbar.set_label('Sample Count', fontsize=8.5, color=COLOR_SLATE)

    # Ticks & Labels
    ax.set(xticks=np.arange(len(CLASSES_SHORT)),
           yticks=np.arange(len(CLASSES_SHORT)),
           xticklabels=CLASSES_SHORT, yticklabels=CLASSES_SHORT)
    ax.tick_params(axis='both', which='major', labelsize=9)
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center")

    ax.set_xlabel('Predicted Statutory Category', fontsize=9.5, fontweight='bold', color=COLOR_NAVY, labelpad=8)
    ax.set_ylabel('Ground Truth Statutory Category', fontsize=9.5, fontweight='bold', color=COLOR_NAVY, labelpad=8)
    ax.set_title(f"{title}\n", fontsize=11, fontweight='bold', color=COLOR_NAVY, pad=12)
    ax.text(0.5, 1.02, subtitle, transform=ax.transAxes, ha='center', fontsize=8.5, fontstyle='italic', color=COLOR_SLATE)

    # Loop over data dimensions and create text annotations
    thresh = np.max(cm) / 2.
    for i in range(len(CLASSES)):
        for j in range(len(CLASSES)):
            count = cm[i, j]
            pct = cm_norm[i, j] * 100
            text_color = "white" if count > thresh else TEXT_DARK
            ax.text(j, i, f"{count}\n({pct:.1f}%)",
                    ha="center", va="center",
                    color=text_color, fontsize=8.5, fontweight='bold')

    plt.tight_layout()
    fig.savefig(out_png, dpi=300, bbox_inches='tight')
    fig.savefig(out_svg, bbox_inches='tight')
    plt.close(fig)
    print(f"Exported {os.path.basename(out_png)} & .svg")

def create_all_confusion_matrices(out_dir):
    # 1. Phase 8E Random Forest Development (N=194)
    cm_8e = np.array([
        [33, 23, 17, 2],
        [25, 31, 12, 7],
        [8,   3, 18, 5],
        [3,   1,  2, 4]
    ])
    plot_academic_cm(cm_8e,
                     'Phase 8E Random Forest Development Benchmark',
                     'Stratified 5-Fold Cross-Validation (N=194, Accuracy=44.33%)',
                     os.path.join(out_dir, 'confusion_matrix_phase8e_rf.png'),
                     os.path.join(out_dir, 'confusion_matrix_phase8e_rf.svg'),
                     194, 0.4433)

    # 2. Phase 10B Qwen3-VL Development Diagnostics (N=16)
    cm_10b = np.array([
        [4, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 2, 4],
        [0, 0, 0, 5]
    ])
    plot_academic_cm(cm_10b,
                     'Phase 10B Qwen3-VL Development Diagnostic Cohort',
                     'Zero-Shot Policy Prompting on A100 GPU (N=16, Accuracy=75.00%)',
                     os.path.join(out_dir, 'confusion_matrix_phase10b_qwen.png'),
                     os.path.join(out_dir, 'confusion_matrix_phase10b_qwen.svg'),
                     16, 0.7500)

    # 3. Phase 10C Hierarchical Fusion Development (N=16)
    cm_10c = np.array([
        [4, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 6, 0],
        [0, 0, 0, 5]
    ])
    plot_academic_cm(cm_10c,
                     'Phase 10C Hierarchical Fusion Development Cohort',
                     'Strategy D Arbitration on Diagnostic Cohort (N=16, Accuracy=100.0%)',
                     os.path.join(out_dir, 'confusion_matrix_phase10c_fusion.png'),
                     os.path.join(out_dir, 'confusion_matrix_phase10c_fusion.svg'),
                     16, 1.0000)

    # 4. Phase 10D Hierarchical Fusion Independent Held-Out Test (N=27)
    cm_10d = np.array([
        [9, 0, 0, 0],
        [8, 1, 0, 0],
        [1, 0, 4, 0],
        [0, 0, 0, 4]
    ])
    plot_academic_cm(cm_10d,
                     'Phase 10D Hierarchical Fusion Independent Held-Out Test',
                     'Strictly Frozen Rules on Unseen Test Split (N=27, Accuracy=66.7%)',
                     os.path.join(out_dir, 'confusion_matrix_phase10d_held_out.png'),
                     os.path.join(out_dir, 'confusion_matrix_phase10d_held_out.svg'),
                     27, 0.6667)

# ==============================================================================
# 5. MODEL PERFORMANCE COMPARISON CHART (PHASE 10D)
# ==============================================================================
def create_model_comparison_chart(out_dir):
    fig, ax = plt.subplots(figsize=(10, 5.8), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')

    metrics = ['4-Class Accuracy', 'Macro-Averaged F1', 'Prohibited Recall', 'Prohibited FAR (Leakage)']
    rf_scores = [37.0, 28.6, 25.0, 75.0]
    qwen_scores = [66.7, 68.9, 100.0, 0.0]
    fusion_scores = [66.7, 68.9, 100.0, 0.0]

    x = np.arange(len(metrics))
    width = 0.25

    rects1 = ax.bar(x - width, rf_scores, width, label='Random Forest (Phase 8E)', color='#94A3B8', edgecolor='#64748B')
    rects2 = ax.bar(x, qwen_scores, width, label='Qwen3-VL-8B (Phase 10B)', color='#6D28D9', edgecolor='#4C1D95')
    rects3 = ax.bar(x + width, fusion_scores, width, label='Strategy D Fusion (Phase 10D)', color='#0F766E', edgecolor='#042F2E')

    ax.set_ylabel('Percentage (%) / Score', fontsize=10, fontweight='bold', color=COLOR_NAVY)
    ax.set_title('Phase 10D Independent Held-Out Test Evaluation Comparison (N=27)\n', fontsize=12, fontweight='bold', color=COLOR_NAVY)
    ax.text(0.5, 1.02, 'Frozen Models Evaluated on Pristine Unseen Ad Creatives', transform=ax.transAxes, ha='center', fontsize=8.5, fontstyle='italic', color=COLOR_SLATE)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=9, fontweight='bold', color=TEXT_DARK)
    ax.legend(loc='upper right', fontsize=8.5, framealpha=0.95)
    ax.set_ylim(0, 115)
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    # Autolabel helper
    for rects in [rects1, rects2, rects3]:
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=7.5, fontweight='bold')

    plt.tight_layout()
    out_png = os.path.join(out_dir, 'model_performance_comparison_phase10d.png')
    out_svg = os.path.join(out_dir, 'model_performance_comparison_phase10d.svg')
    fig.savefig(out_png, dpi=300, bbox_inches='tight')
    fig.savefig(out_svg, bbox_inches='tight')
    plt.close(fig)
    print("Exported model_performance_comparison_phase10d.png & .svg")

# ==============================================================================
# 6. MULTIMODAL ABLATION COMPARISON CHART
# ==============================================================================
def create_multimodal_ablation_chart(out_dir):
    fig, ax = plt.subplots(figsize=(9, 5.2), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')

    modalities = ['Text Only\n(RoBERTa)', 'Audio Only\n(Whisper ASR)', 'Video Only\n(VideoMAE)', 'Learned Late Fusion\n(RF 33-Dim)', 'VLM Reasoning\n(Qwen3-VL 8B)']
    accuracies = [35.1, 28.4, 38.2, 44.33, 66.7]
    colors = ['#CBD5E1', '#CBD5E1', '#CBD5E1', '#3B82F6', '#0F766E']

    bars = ax.bar(modalities, accuracies, width=0.55, color=colors, edgecolor='#475569', linewidth=1.0)
    ax.set_ylabel('Four-Class Accuracy (%)', fontsize=10, fontweight='bold', color=COLOR_NAVY)
    ax.set_title('Modality Ablation Study: Unimodal Baselines vs. Multimodal Fusion\n', fontsize=11, fontweight='bold', color=COLOR_NAVY)
    ax.text(0.5, 1.02, 'Empirical Demonstration of Cross-Modal Concealment Resolution', transform=ax.transAxes, ha='center', fontsize=8.5, fontstyle='italic', color=COLOR_SLATE)
    ax.set_ylim(0, 80)
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8.5, fontweight='bold')

    plt.tight_layout()
    out_png = os.path.join(out_dir, 'multimodal_modality_ablation_chart.png')
    out_svg = os.path.join(out_dir, 'multimodal_modality_ablation_chart.svg')
    fig.savefig(out_png, dpi=300, bbox_inches='tight')
    fig.savefig(out_svg, bbox_inches='tight')
    plt.close(fig)
    print("Exported multimodal_modality_ablation_chart.png & .svg")

# ==============================================================================
# 7. GPU LATENCY & MEMORY USAGE PROFILE
# ==============================================================================
def create_gpu_latency_memory_profile(out_dir):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')

    stages = ['Optical Flow', 'EasyOCR', 'Whisper ASR', 'Falcon NSFW', 'RF Fusion', 'Qwen3-VL VLM', 'ArcFace + PAD']
    latencies = [124.5, 210.8, 340.2, 45.1, 2.4, 820.6, 58.3]
    vram = [450, 1280, 1640, 820, 10, 16400, 980]

    # Subplot 1: Latency (ms)
    y_pos = np.arange(len(stages))
    bars1 = ax1.barh(y_pos, latencies, color='#1E3A8A', edgecolor='#0F172A', height=0.6)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(stages, fontsize=8.5, fontweight='bold')
    ax1.invert_yaxis()
    ax1.set_xlabel('Mean Execution Latency (ms)', fontsize=9.5, fontweight='bold', color=COLOR_NAVY)
    ax1.set_title('Component Latency Breakdown (A100 GPU)', fontsize=10.5, fontweight='bold', color=COLOR_NAVY)
    ax1.grid(axis='x', linestyle='--', alpha=0.3)
    for bar in bars1:
        w = bar.get_width()
        ax1.text(w + 15, bar.get_y() + bar.get_height()/2, f'{w:.1f} ms',
                 ha='left', va='center', fontsize=7.5, color=TEXT_DARK)
    ax1.set_xlim(0, 1000)

    # Subplot 2: VRAM Footprint (MB)
    bars2 = ax2.barh(y_pos, vram, color='#0F766E', edgecolor='#042F2E', height=0.6)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([''] * len(stages))
    ax2.invert_yaxis()
    ax2.set_xlabel('GPU VRAM Allocation (MB)', fontsize=9.5, fontweight='bold', color=COLOR_NAVY)
    ax2.set_title('GPU Memory Footprint Profile (bfloat16)', fontsize=10.5, fontweight='bold', color=COLOR_NAVY)
    ax2.grid(axis='x', linestyle='--', alpha=0.3)
    for bar in bars2:
        w = bar.get_width()
        ax2.text(w + 250, bar.get_y() + bar.get_height()/2, f'{w:,} MB',
                 ha='left', va='center', fontsize=7.5, color=TEXT_DARK)
    ax2.set_xlim(0, 19500)

    plt.tight_layout()
    out_png = os.path.join(out_dir, 'gpu_latency_memory_profile.png')
    out_svg = os.path.join(out_dir, 'gpu_latency_memory_profile.svg')
    fig.savefig(out_png, dpi=300, bbox_inches='tight')
    fig.savefig(out_svg, bbox_inches='tight')
    plt.close(fig)
    print("Exported gpu_latency_memory_profile.png & .svg")

def main():
    chart_dir = os.path.join('report_assets_final', 'evaluation_charts')
    os.makedirs(chart_dir, exist_ok=True)

    create_all_confusion_matrices(chart_dir)
    create_model_comparison_chart(chart_dir)
    create_multimodal_ablation_chart(chart_dir)
    create_gpu_latency_memory_profile(chart_dir)

if __name__ == '__main__':
    main()
