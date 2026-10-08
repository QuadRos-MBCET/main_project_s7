import os
import sys

# Detect environment: Colab vs Local
IS_COLAB = "google.colab" in sys.modules or os.path.exists("/content")

# Base directory setup
if IS_COLAB:
    DRIVE_MOUNT_PATH = "/content/drive/MyDrive/SafeAdAI"
    BASE_DIR = DRIVE_MOUNT_PATH if os.path.exists(DRIVE_MOUNT_PATH) else "/content/SafeAdAI"
else:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Directories
MODEL_DIR = os.path.join(BASE_DIR, "checkpoints")
DATASET_DIR = os.path.join(BASE_DIR, "datasets")
EMBEDDING_DIR = os.path.join(BASE_DIR, "embeddings")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
LOG_DIR = os.path.join(BASE_DIR, "logs")

for path in [MODEL_DIR, DATASET_DIR, EMBEDDING_DIR, OUTPUT_DIR, LOG_DIR]:
    os.makedirs(path, exist_ok=True)

try:
    import torch
    HAS_TORCH = True
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    CUDA_AVAILABLE = torch.cuda.is_available()
except ImportError:
    HAS_TORCH = False
    DEVICE = "cpu"
    CUDA_AVAILABLE = False

VRAM_SAFETY_LIMIT_MB = 12000 if IS_COLAB else 4000  # Threshold for warning/unloading

# Video Processing Config
MAX_VIDEO_FRAMES = 16
FRAME_SAMPLE_STRATEGY = "uniform"  # "uniform", "keyframe", "temporal"

# Model Execution Config
MIXED_PRECISION_ENABLED = True
BATCH_SIZE = 1  # Colab Free optimal batch size

# Audio Processing Config
WHISPER_MODEL = "base"  # Options: "tiny", "base", "small" (optimal for Google Colab Free)
AUDIO_SAMPLE_RATE = 16000
AUDIO_CACHE_DIR = os.path.join(OUTPUT_DIR, "audio_cache")
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)

print(f"[SafeAd AI Config] Environment: {'Google Colab' if IS_COLAB else 'Local Machine'}")
print(f"[SafeAd AI Config] Execution Device: {DEVICE} (CUDA Available: {CUDA_AVAILABLE})")


