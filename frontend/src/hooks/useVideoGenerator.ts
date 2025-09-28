import { useState } from 'react';
import { videoService } from '@/services/video.service';
import type { VideoGenerationOptions, VideoJobInfo, VideoJobStatus } from '@/types/video.types';
import type { GenerationStatus } from '@/types';
import { sleep } from '@/utils/async.utils';

export function useVideoGenerator() {
  const [status, setStatus] = useState<GenerationStatus>('idle');
  const [statusText, setStatusText] = useState<VideoJobStatus | null>(null);
  const [result, setResult] = useState<VideoJobInfo | null>(null);
  const [error, setError] = useState<string | null>(null);

  const generate = async (file: File, options: VideoGenerationOptions) => {
    setStatus('loading');
    setError(null);
    setResult(null);
    setStatusText('queued');

    try {
      const job = await videoService.generateFromUpload(file, options);
      
      if (!job?.job_id) {
        throw new Error('Failed to start video job');
      }

      let pollMs = (job.poll_interval_s ?? 2) * 1000;
      let tries = 0;
      const MAX_RETRIES = 100;

      while (tries < MAX_RETRIES) {
        await sleep(pollMs);
        
        try {
          const info = await videoService.getJobStatus(job.job_id);
          setStatusText(info.status);

          if (info.status === 'done') {
            setResult(info);
            setStatus('success');
            break;
          }
          
          if (info.status === 'error') {
            throw new Error(info.error || 'Video job failed');
          }

          tries++;
          if (tries % 8 === 0) {
            pollMs = Math.min(pollMs + 500, 5000);
          }
        } catch (e) {
          tries++;
          if (tries % 5 === 0) {
            pollMs = Math.min(pollMs + 1000, 7000);
          }
          
          if (tries >= MAX_RETRIES) {
            throw e;
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate video');
      setStatus('error');
    }
  };

  return {
    generate,
    status,
    statusText,
    result,
    error,
    isLoading: status === 'loading',
  };
}
