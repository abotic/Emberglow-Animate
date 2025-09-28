import { VideoGenerationOptions, VideoJob, VideoJobInfo } from '../types/video.types';
import { apiClient } from './api.client';

class VideoService {
  async generateFromUpload(
    file: File, 
    options: VideoGenerationOptions
  ): Promise<VideoJob> {
    const formData = new FormData();
    formData.append('file', file);

    const params = new URLSearchParams({
      video_type: options.video_type,
      enhance_quality: String(options.enhance_quality),
      create_loop: String(options.create_loop),
      base_seconds: String(options.base_seconds),
      fps: String(options.fps),
      duration_minutes: String(options.duration_minutes),
      async: '1',
    });

    return apiClient.post(`/api/video/generate_loop_from_upload?${params}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  }

  async getJobStatus(jobId: string): Promise<VideoJobInfo> {
    return apiClient.get(`/api/video/job/${jobId}`);
  }

  async warmup(): Promise<{ ok: boolean }> {
    return apiClient.post('/api/video/warmup');
  }
}

export const videoService = new VideoService();