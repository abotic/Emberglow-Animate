from ..models.image_model import ImageModelManager
from .config import get_settings

settings = get_settings()

image_manager = ImageModelManager(hf_token=settings.hf_token)

# TODO disabling video until it is polished
# video_manager = VideoModelManager(hf_token=settings.hf_token)