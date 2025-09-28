import { ImageGenerationParams, ImageGenerationResponse } from '../types/image.types';
import { apiClient } from './api.client';

class ImageService {
  async generate(params: ImageGenerationParams): Promise<ImageGenerationResponse> {
    return apiClient.post('/api/image/generate', params);
  }

  async warmup(): Promise<{ ok: boolean }> {
    return apiClient.post('/api/image/warmup');
  }
}

export const imageService = new ImageService();