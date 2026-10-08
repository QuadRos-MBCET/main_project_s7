try:
    import torch
except ImportError:
    torch = None
from ai.memory_manager import MemoryManager
from ai.config import DEVICE

class ModelManager:
    """
    Manages lazy loading, caching, and explicit unloading of AI models
    to stay strictly within Google Colab Free VRAM/RAM constraints.
    """
    def __init__(self):
        self.model_cache = {}
        
    def get_model(self, model_key: str, loader_fn):
        """
        Retrieves model from cache or loads it using loader_fn if not present.
        """
        if model_key in self.model_cache:
            return self.model_cache[model_key]
            
        print(f"[ModelManager] Loading model component '{model_key}' onto {DEVICE}...")
        
        # Check memory safety before loading heavy models
        if not MemoryManager.check_vram_sufficient(required_mb=500):
            print(f"[ModelManager WARNING] Low VRAM detected before loading '{model_key}'. Evicting unused cached models...")
            self.clear_all_except(keep_keys=[])
            
        try:
            model = loader_fn()
            self.model_cache[model_key] = model
            return model
        except Exception as e:
            print(f"[ModelManager ERROR] Failed to load model '{model_key}': {e}")
            MemoryManager.clear_gpu_memory()
            return None

    def unload(self, model_key: str):
        """Unloads a single model component from memory."""
        if model_key in self.model_cache:
            print(f"[ModelManager] Unloading '{model_key}' from GPU/RAM...")
            model = self.model_cache.pop(model_key)
            MemoryManager.unload_model(model)

    def clear_all_except(self, keep_keys: list = None):
        """Clears all cached models except those in keep_keys."""
        keep_keys = keep_keys or []
        keys_to_remove = [k for k in self.model_cache.keys() if k not in keep_keys]
        for k in keys_to_remove:
            self.unload(k)
        MemoryManager.clear_gpu_memory()

# Global Singleton instance
model_manager = ModelManager()
