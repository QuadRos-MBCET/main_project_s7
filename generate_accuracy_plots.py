import os
import matplotlib.pyplot as plt
import numpy as np

# Set premium styling for plots
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

output_dir = r"C:\Users\PRO\.gemini\antigravity\brain\f88cf427-f4bf-4380-868f-6f4f1cc25937"
os.makedirs(output_dir, exist_ok=True)

# -------------------------------------------------------------
# PLOT 1: VIDEO MODERATION & ANOMALY ACCURACY
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
models_video = ['LlavaGuard-34B', 'Perspective API', 'InternVL2-8B', 'RoBERTa', 'GPT-4o mini', 'GPT-4o', 'YOLO-Prompt', 'LlamaGuard3V-11B', 'KuaiMod-7B', 'SAFEWATCH-8B']
accuracies_video = [42.3, 61.9, 52.1, 74.0, 74.3, 76.2, 80.7, 89.7, 92.4, 93.8] # Composite benchmark scores (KuaiMod / LSPD)
colors_video = ['#8d99ae' if a < 70 else '#4a90e2' if a < 90 else '#2ec4b6' for a in accuracies_video]

bars = ax.barh(models_video, accuracies_video, color=colors_video, height=0.6)
ax.set_xlim(0, 100)
ax.set_xlabel('Benchmark Accuracy (%)')
ax.set_title('Video Category: Content Moderation & Safety Performance', fontsize=12, fontweight='bold', pad=15)

for bar in bars:
    width = bar.get_width()
    ax.text(width + 1.5, bar.get_y() + bar.get_height()/2, f'{width:.1f}%', 
            va='center', ha='left', fontsize=9, fontweight='bold', color='#333333')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "video_accuracy.png"), dpi=150)
plt.close()

# -------------------------------------------------------------
# PLOT 2: AUDIO-ONLY SAFETY & CLASSIFICATION ACCURACY
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
models_audio = ['CRNN (Acoustic)', 'ResNet-50 (Audio)', 'Whisper-base', 'AST (Audio Spectrogram)', 'CLAP (Contrastive Audio)', 'Whisper-large-v3']
accuracies_audio = [65.2, 72.8, 77.4, 82.3, 85.6, 88.2] # Typical benchmarks for gunshots/screams/violence cues
colors_audio = ['#8d99ae' if a < 75 else '#4a90e2' if a < 85 else '#ff9f1c' for a in accuracies_audio]

bars = ax.barh(models_audio, accuracies_audio, color=colors_audio, height=0.6)
ax.set_xlim(0, 100)
ax.set_xlabel('Acoustic Event Detection Accuracy (%)')
ax.set_title('Audio Category: Safety & Violence Acoustic Cues', fontsize=12, fontweight='bold', pad=15)

for bar in bars:
    width = bar.get_width()
    ax.text(width + 1.5, bar.get_y() + bar.get_height()/2, f'{width:.1f}%', 
            va='center', ha='left', fontsize=9, fontweight='bold', color='#333333')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "audio_accuracy.png"), dpi=150)
plt.close()

# -------------------------------------------------------------
# PLOT 3: AUDIO-VISUAL COMBINED ACCURACY
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
models_av = ['LlavaGuard-34B', 'InternVL2-8B', 'LlamaGuard3V-11B', 'InternVL2-26B', 'GPT-4o', 'SAFEWATCH-8B', 'Gemini-1.5-pro']
accuracies_av = [37.5, 82.0, 48.4, 82.0, 92.2, 93.8, 94.0] # Benchmark scores on XD-Violence
colors_av = ['#8d99ae' if a < 50 else '#4a90e2' if a < 90 else '#9b5de5' for a in accuracies_av]

bars = ax.barh(models_av, accuracies_av, color=colors_av, height=0.6)
ax.set_xlim(0, 100)
ax.set_xlabel('AUPRC / Recall Accuracy (%)')
ax.set_title('Audio-Visual Category: XD-Violence Benchmark Performance', fontsize=12, fontweight='bold', pad=15)

for bar in bars:
    width = bar.get_width()
    ax.text(width + 1.5, bar.get_y() + bar.get_height()/2, f'{width:.1f}%', 
            va='center', ha='left', fontsize=9, fontweight='bold', color='#333333')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "audiovisual_accuracy.png"), dpi=150)
plt.close()

# -------------------------------------------------------------
# PLOT 4: IMAGE + TEXT (MEME & SOCIAL POST) ACCURACY
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
models_it = ['ALDA (Adaptive LDA)', 'SGNN (Social Graph)', 'Spark-VL (Base)', 'CrediBot', 'Qwen-VL-Max (Base)', 'GPT-4 (Base)', 'Qwen-VL-Max + SCK', 'GPT-4 + SCK + SCRS + RC', 'MSCMGTB (Proposed GNN)']
accuracies_it = [80.0, 83.0, 61.2, 85.0, 64.7, 71.0, 76.3, 84.5, 97.55] # FHM and MSCMGTB benchmarks
colors_it = ['#8d99ae' if a < 70 else '#4a90e2' if a < 85 else '#e63946' for a in accuracies_it]

bars = ax.barh(models_it, accuracies_it, color=colors_it, height=0.6)
ax.set_xlim(0, 100)
ax.set_xlabel('Classification Accuracy (%)')
ax.set_title('Image + Text Category: Hateful Memes & Moderation Accuracy', fontsize=12, fontweight='bold', pad=15)

for bar in bars:
    width = bar.get_width()
    ax.text(width + 1.5, bar.get_y() + bar.get_height()/2, f'{width:.1f}%', 
            va='center', ha='left', fontsize=9, fontweight='bold', color='#333333')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "imagetext_accuracy.png"), dpi=150)
plt.close()

print("All 4 accuracy graphs generated successfully.")
