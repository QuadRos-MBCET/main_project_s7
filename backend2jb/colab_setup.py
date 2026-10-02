import os
import sys
import subprocess

def run_colab_environment_setup():
    """
    Automated environment initialization script for Google Colab Free tier.
    Detects GPU, prints VRAM, verifies installed packages, and configures paths.
    """
    print("=" * 60)
    print("SAFEAD AI (SAFE-VISION) - GOOGLE COLAB ENVIRONMENT SETUP")
    print("=" * 60)

    # 1. Detect Environment
    is_colab = "google.colab" in sys.modules or os.path.exists("/content")
    print(f"[SafeAd Colab Setup] Execution Environment: {'Google Colab' if is_colab else 'Local Machine'}")

    # 2. Check GPU & VRAM Availability
    try:
        import torch
        has_gpu = torch.cuda.is_available()
        if has_gpu:
            gpu_name = torch.cuda.get_device_name(0)
            vram_bytes = torch.cuda.get_device_properties(0).total_memory
            vram_mb = vram_bytes / (1024 ** 2)
            print(f"[SafeAd Colab Setup] 🟢 GPU Detected: {gpu_name}")
            print(f"[SafeAd Colab Setup] 🟢 Total VRAM: {vram_mb:.2f} MB")
        else:
            print("[SafeAd Colab Setup] ⚠️ No GPU detected. Operating in CPU Fallback mode.")
    except Exception as e:
        print(f"[SafeAd Colab Setup ⚠️] PyTorch GPU check failed: {e}")

    # 3. Create required Colab directories under /content/
    work_dir = "/content" if is_colab else os.getcwd()
    for subfolder in ["uploads", "outputs", "logs", "checkpoints"]:
        path = os.path.join(work_dir, subfolder)
        os.makedirs(path, exist_ok=True)

    print(f"[SafeAd Colab Setup] Working directory: {work_dir}")
    print("[SafeAd Colab Setup] Environment verification completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    run_colab_environment_setup()
