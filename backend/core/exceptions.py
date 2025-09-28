from typing import Optional, Dict, Any

class BaseAPIException(Exception):
    def __init__(
        self, 
        message: str, 
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

class ModelLoadError(BaseAPIException):
    def __init__(self, message: str):
        super().__init__(message, status_code=500)

class GenerationError(BaseAPIException):
    def __init__(self, message: str):
        super().__init__(message, status_code=500)

class ValidationError(BaseAPIException):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)