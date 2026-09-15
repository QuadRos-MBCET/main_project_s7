import torch
import gc

class ModelManager:
    @staticmethod
    def get_device():
        return torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    @staticmethod
    def clear_memory():
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
