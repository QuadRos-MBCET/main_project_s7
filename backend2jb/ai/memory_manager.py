import gc
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

from ai.config import DEVICE, VRAM_SAFETY_LIMIT_MB

class MemoryManager:
    @staticmethod
    def get_gpu_memory_info() -> dict:
        """Returns GPU VRAM stats in MB if CUDA is available."""
        if not HAS_TORCH or not torch.cuda.is_available():
            return {
                "cuda_available": False,
                "device_name": "CPU",
                "total_mb": 0,
                "allocated_mb": 0,
                "reserved_mb": 0,
                "free_mb": 0
            }
            
        device_idx = torch.cuda.current_device()
        total_b = torch.cuda.get_device_properties(device_idx).total_memory
        allocated_b = torch.cuda.memory_allocated(device_idx)
        reserved_b = torch.cuda.memory_reserved(device_idx)
        free_b = total_b - allocated_b
        
        return {
            "cuda_available": True,
            "device_name": torch.cuda.get_device_name(device_idx),
            "total_mb": round(total_b / (1024 ** 2), 2),
            "allocated_mb": round(allocated_b / (1024 ** 2), 2),
            "reserved_mb": round(reserved_b / (1024 ** 2), 2),
            "free_mb": round(free_b / (1024 ** 2), 2)
        }

    @staticmethod
    def print_resource_status():
        info = MemoryManager.get_gpu_memory_info()
        print("=" * 60)
        print("          RESOURCE & GPU MEMORY STATUS MONITOR          ")
        print("=" * 60)
        print(f"CUDA Available : {info['cuda_available']}")
        print(f"Device Name    : {info['device_name']}")
        if info['cuda_available']:
            print(f"Total VRAM     : {info['total_mb']} MB")
            print(f"Allocated VRAM : {info['allocated_mb']} MB")
            print(f"Reserved VRAM  : {info['reserved_mb']} MB")
            print(f"Free VRAM      : {info['free_mb']} MB")
        print("=" * 60)

    @staticmethod
    def clear_gpu_memory():
        """Forces Python garbage collection and PyTorch CUDA cache release."""
        gc.collect()
        if HAS_TORCH and torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

    @staticmethod
    def unload_model(model_obj):
        """Moves model to CPU and deletes reference to release VRAM."""
        if model_obj is not None:
            try:
                if hasattr(model_obj, "to"):
                    model_obj.to("cpu")
            except Exception:
                pass
            del model_obj
        MemoryManager.clear_gpu_memory()

    @staticmethod
    def check_vram_sufficient(required_mb: int = 1000) -> bool:
        """Returns True if free VRAM exceeds required_mb, or if running on CPU."""
        if not HAS_TORCH or not torch.cuda.is_available():
            return True
        info = MemoryManager.get_gpu_memory_info()
        return info["free_mb"] >= required_mb

