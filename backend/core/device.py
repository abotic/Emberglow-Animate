import torch
from typing import Literal

DeviceType = Literal["cuda", "mps", "cpu"]

class DeviceManager:
    @staticmethod
    def get_device() -> DeviceType:
        if torch.cuda.is_available():
            return "cuda"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    
    @staticmethod
    def get_dtype(device: DeviceType, force_fp16: bool = True) -> torch.dtype:
        if device == "cuda" and force_fp16:
            return torch.float16
        return torch.float32
    
    @staticmethod
    def setup_cuda_optimizations() -> None:
        if torch.cuda.is_available():
            torch.set_float32_matmul_precision("high")
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True