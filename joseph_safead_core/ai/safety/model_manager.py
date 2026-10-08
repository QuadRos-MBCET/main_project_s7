import gc
import contextlib
from typing import Dict, Any, Optional

try:
    import torch
    HAS_TORCH = True
except ImportError:
    torch = None
    HAS_TORCH = False

from ai.memory_manager import MemoryManager
from ai.config import DEVICE

class SafetyModelManager:
    """
    Model Manager designed specifically for Google Colab Free memory constraints.
    Enforces sequential model loading, lazy loading, model caching, and automatic VRAM release.
    """

    def __init__(self):
        self._models: Dict[str, Any] = {}
        self._loaders: Dict[str, Any] = {}
        self._status: Dict[str, str] = {
            "violence": "unloaded",
            "nsfw": "unloaded",
            "child_safety": "unloaded"
        }

    def register_loader(self, model_name: str, loader_fn):
        """Registers a factory function for loading a specific safety model."""
        self._loaders[model_name] = loader_fn

    def get_gpu_memory(self) -> Dict[str, Any]:
        """Returns current GPU VRAM usage via MemoryManager."""
        return MemoryManager.get_gpu_memory_info()

    def get_model_status(self) -> Dict[str, str]:
        """Returns current status of registered models."""
        return dict(self._status)

    def load_model(self, model_name: str) -> Optional[Any]:
        """
        Loads a single model into memory. Evicts other models if VRAM is low.
        """
        if model_name in self._models and self._models[model_name] is not None:
            return self._models[model_name]

        if model_name not in self._loaders:
            print(f"[SafetyModelManager WARNING] No loader registered for model '{model_name}'.")
            return None

        # Clean VRAM before loading new model
        MemoryManager.clear_gpu_memory()

        print(f"[SafetyModelManager] Loading model '{model_name}' on {DEVICE}...")
        try:
            try:
                model = self._loaders[model_name]()
            except TypeError:
                model = self._loaders[model_name](model_name)
            self._models[model_name] = model
            self._status[model_name] = "loaded"
            return model
        except Exception as e:
            print(f"[SafetyModelManager ERROR] Failed to load model '{model_name}': {e}")
            self._status[model_name] = f"error: {e}"
            MemoryManager.clear_gpu_memory()
            return None

    def release_model(self, model_name: str):
        """Releases a specific model from GPU and RAM."""
        if model_name in self._models:
            print(f"[SafetyModelManager] Releasing model '{model_name}' from VRAM/RAM...")
            model = self._models.pop(model_name)
            MemoryManager.unload_model(model)
            self._status[model_name] = "unloaded"
        MemoryManager.clear_gpu_memory()

    def release_all_models(self):
        """Releases all models currently loaded in memory."""
        for model_name in list(self._models.keys()):
            self.release_model(model_name)
        MemoryManager.clear_gpu_memory()

    @contextlib.contextmanager
    def use(self, model_name: str):
        """
        Context manager for sequential execution.
        Loads the specified model, yields control, and automatically releases VRAM upon exiting.

        Example:
            with safety_model_manager.use("violence") as model:
                res = model.predict(video)
        """
        # Ensure strict sequential isolation: unload any other loaded models first
        for loaded_name in list(self._models.keys()):
            if loaded_name != model_name:
                self.release_model(loaded_name)

        model = self.load_model(model_name)
        try:
            yield model
        finally:
            self.release_model(model_name)

# Global singleton instance
safety_model_manager = SafetyModelManager()
