import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import shutil
import os

# 1. Copy use_case_diagram.jpg to safead_use_case_diagram.png
if os.path.exists("overleaf_figures/use_case_diagram.jpg"):
    shutil.copy2("overleaf_figures/use_case_diagram.jpg", "overleaf_figures/safead_use_case_diagram.png")
    shutil.copy2("overleaf_figures/use_case_diagram.jpg", "safead_use_case_diagram.png")
    print("Copied use_case_diagram to safead_use_case_diagram.png")

# 2. Create high-resolution Presentation Attack Detection Interception HUD (spoof.png)
def create_spoof_hud():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.5)
    ax.axis('off')
    fig.patch.set_facecolor('#0B0F19') # Dark HUD background

    # HUD Outer Frame
    outer = patches.Rectangle((0.2, 0.2), 9.6, 6.1, facecolor='#111827', edgecolor='#EF4444', linewidth=2.5)
    ax.add_patch(outer)

    # Header Bar
    head = patches.Rectangle((0.2, 5.7), 9.6, 0.6, facecolor='#7F1D1D')
    ax.add_patch(head)
    ax.text(5.0, 6.0, 'ALERT: PRESENTATION ATTACK INTERCEPTED (SPOOF DETECTED)',
            ha='center', va='center', fontsize=12, fontweight='bold', color='#FCA5A5')

    # Video Feed Simulation Box (Left)
    feed_bg = patches.Rectangle((0.5, 0.5), 5.6, 5.0, facecolor='#1F2937', edgecolor='#374151', linewidth=1.5)
    ax.add_patch(feed_bg)

    # Face bounding box (Red - flagged)
    face_box = patches.Rectangle((1.6, 1.8), 3.4, 3.2, facecolor='none', edgecolor='#EF4444', linewidth=2.5, linestyle='--')
    ax.add_patch(face_box)
    ax.text(3.3, 5.15, 'SPOOF REPLAY DETECTED', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#EF4444')

    # Hough Line bezel markers (Green screen border segments detected)
    for y_line in [1.5, 4.8]:
        ax.plot([1.2, 5.4], [y_line, y_line], color='#10B981', linewidth=2, linestyle=':')
    for x_line in [1.2, 5.4]:
        ax.plot([x_line, x_line], [1.5, 4.8], color='#10B981', linewidth=2, linestyle=':')
    ax.text(3.3, 1.35, 'Hough Screen Border Bezel Segments: 48 detected', ha='center', va='center', fontsize=8, color='#34D399')

    # Specular glare / 2D FFT moire indicator
    ax.text(3.3, 2.5, '[2D FFT Moiré Pattern Peak]', ha='center', va='center', fontsize=8.5, color='#FCD34D', fontstyle='italic')

    # Right Telemetry Panel
    tel_bg = patches.Rectangle((6.3, 0.5), 3.3, 5.0, facecolor='#1F2937', edgecolor='#374151', linewidth=1.2)
    ax.add_patch(tel_bg)
    ax.text(7.95, 5.2, 'BIOMETRIC TELEMETRY', ha='center', va='center', fontsize=10, fontweight='bold', color='#E5E7EB')

    metrics = [
        ('MiniFASNet PAD Score:', '0.940 (SPOOF)', '#EF4444'),
        ('Operating Threshold:', 'tau_pad = 0.500', '#9CA3AF'),
        ('Attack Classification:', '2D Screen Replay (iPad)', '#F87171'),
        ('Specular Reflection:', 'Flagged (Glass Glare)', '#FBBF24'),
        ('High-Freq FFT Power:', 'Flagged (0.887)', '#FBBF24'),
        ('ArcFace Cosine Match:', '0.688 (Matched)', '#60A5FA'),
        ('Biometric State:', 'REJECTED: UNTRUSTED', '#EF4444'),
        ('Delivery Action:', 'CONTENT SUPPRESSED', '#EF4444'),
    ]

    y_pos = 4.6
    for k, v, col in metrics:
        ax.text(6.5, y_pos, k, fontsize=7.8, color='#D1D5DB')
        ax.text(6.5, y_pos - 0.25, v, fontsize=8.2, fontweight='bold', color=col)
        y_pos -= 0.52

    plt.tight_layout()
    plt.savefig('overleaf_figures/spoof.png', dpi=300, bbox_inches='tight')
    plt.savefig('spoof.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Created spoof.png")

# 3. Create Institutional College Emblem Crest (mbcetlogo.png)
def create_mbcet_logo():
    fig, ax = plt.subplots(figsize=(4, 4), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    # Circular crest
    outer_circle = plt.Circle((5, 5), 4.6, color='#1E3A8A', fill=True)
    inner_circle = plt.Circle((5, 5), 4.2, color='#FFFFFF', fill=True)
    center_circle = plt.Circle((5, 5), 3.0, color='#1E3A8A', fill=False, linewidth=2)
    ax.add_patch(outer_circle)
    ax.add_patch(inner_circle)
    ax.add_patch(center_circle)

    # Core Emblem text
    ax.text(5, 7.8, 'MAR BASELIOS COLLEGE', ha='center', va='center', fontsize=9, fontweight='bold', color='#1E3A8A')
    ax.text(5, 7.1, 'OF ENGINEERING AND TECHNOLOGY', ha='center', va='center', fontsize=7, fontweight='bold', color='#1E3A8A')
    ax.text(5, 5.3, 'MBCET', ha='center', va='center', fontsize=18, fontweight='bold', color='#1E3A8A')
    ax.text(5, 4.3, 'ESTD 2002', ha='center', va='center', fontsize=8, fontweight='bold', color='#B45309')
    ax.text(5, 2.5, 'THIRUVANANTHAPURAM', ha='center', va='center', fontsize=8, fontweight='bold', color='#1E3A8A')
    ax.text(5, 1.8, 'AUTONOMOUS', ha='center', va='center', fontsize=7.5, color='#475569')

    plt.tight_layout()
    plt.savefig('overleaf_figures/mbcetlogo.png', dpi=300, bbox_inches='tight')
    plt.savefig('mbcetlogo.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Created mbcetlogo.png")

create_spoof_hud()
create_mbcet_logo()

# Re-zip
import zipfile, glob
fig_files = glob.glob('overleaf_figures/*')
with zipfile.ZipFile('overleaf_figures.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    for f in sorted(fig_files):
        zipf.write(f, os.path.basename(f))

print(f"Updated overleaf_figures.zip: {os.path.getsize('overleaf_figures.zip'):,} bytes across {len(fig_files)} figures.")
