from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
from functools import lru_cache
import os

class Settings(BaseSettings):
    hf_token: Optional[str] = Field(None, env="HF_TOKEN")
    hf_home: str = Field("models", env="HF_HOME")
    
    api_key: Optional[str] = Field(None, env="API_KEY")
    
    cors_origins: str = Field("*", env="CORS_ORIGINS")
    
    output_dir: str = Field("outputs", env="OUTPUT_DIR")
    temp_dir: str = Field("tmp", env="TEMP_DIR")
    
    auto_warmup: bool = Field(True, env="AUTO_WARMUP")
    force_fp16: bool = Field(True, env="FORCE_FP16")
    disable_xformers: bool = Field(True, env="DISABLE_XFORMERS")
    
    allow_expandable_segments: bool = Field(False, env="ALLOW_EXPANDABLE_SEGMENTS")
    cuda_alloc_conf: str = Field("max_split_size_mb:512", env="PYTORCH_CUDA_ALLOC_CONF")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = 'ignore'
    
    def setup_environment(self) -> None:
        """Configure environment variables for PyTorch"""
        os.environ["HF_HOME"] = self.hf_home
        os.environ["TRANSFORMERS_CACHE"] = self.hf_home
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = self.cuda_alloc_conf
        os.environ.setdefault("CUDA_DEVICE_MAX_CONNECTIONS", "1")
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.hf_home, exist_ok=True)

@lru_cache()
def get_settings() -> Settings:
    return Settings()