import gc
import contextlib
from typing import Dict, Any, Optional

try:
    import torch
    HAS_TORCH = True
except ImportError:
    torch = None
    HAS_TORCH = False

class SafeAdModelManager:
    """
    Model Lifecycle Manager designed specifically for Google Colab Free memory constraints.
    Enforces sequential model loading, lazy loading, and explicit VRAM cache clearing after each stage.
    """

    def __init__(self):
        self._models: Dict[str, Any] = {}
        self._loaders: Dict[str, Any] = {}
        self._status: Dict[str, str] = {}

    def register_loader(self, model_name: str, loader_fn):
        """Registers a loader factory function for a specific model."""
        self._loaders[model_name] = loader_fn
        self._status[model_name] = "unloaded"

    @staticmethod
    def clear_gpu_memory():
        """Frees unreferenced objects and flushes CUDA VRAM cache."""
        gc.collect()
        if HAS_TORCH and torch.cuda.is_available():
            try:
                torch.cuda.empty_cache()
                if hasattr(torch.cuda, "ipc_collect"):
                    torch.cuda.ipc_collect()
            except Exception:
                pass

    def load_model(self, model_name: str) -> Optional[Any]:
        """Loads a model into memory lazily. Clears VRAM beforehand."""
        if model_name in self._models and self._models[model_name] is not None:
            return self._models[model_name]

        if model_name not in self._loaders:
            print(f"[SafeAdModelManager WARNING] Loader for '{model_name}' not registered.")
            return None

        self.clear_gpu_memory()
        print(f"[SafeAdModelManager] Loading model '{model_name}'...")
        try:
            model = self._loaders[model_name]()
            self._models[model_name] = model
            self._status[model_name] = "loaded"
            return model
        except Exception as e:
            print(f"[SafeAdModelManager ERROR] Failed to load model '{model_name}': {e}")
            self._status[model_name] = f"error: {e}"
            self.clear_gpu_memory()
            return None

    def release_model(self, model_name: str):
        """Releases a specific model from GPU/RAM."""
        if model_name in self._models:
            print(f"[SafeAdModelManager] Unloading model '{model_name}' from VRAM...")
            model = self._models.pop(model_name)
            del model
            self._status[model_name] = "unloaded"
        self.clear_gpu_memory()

    def release_all_models(self):
        """Unloads all currently loaded models."""
        for model_name in list(self._models.keys()):
            self.release_model(model_name)
        self.clear_gpu_memory()

    @contextlib.contextmanager
    def sequential_stage(self, model_name: str):
        """
        Context manager for sequential inference stages.
        Unloads any previous model, yields control for inference, and automatically unloads model from VRAM upon exit.
        """
        # Ensure only 1 large model is in VRAM at any given time
        for loaded_name in list(self._models.keys()):
            if loaded_name != model_name:
                self.release_model(loaded_name)

        model = self.load_model(model_name)
        try:
            yield model
        finally:
            self.release_model(model_name)

# Global model manager instance
model_manager = SafeAdModelManager()
