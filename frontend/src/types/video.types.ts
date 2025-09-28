export interface VideoGenerationOptions {
    video_type: 'ambient_loop';
    enhance_quality: boolean;
    create_loop: boolean;
    base_seconds: number;
    fps: number;
    duration_minutes: number;
  }
  
  export interface VideoJob {
    job_id: string;
    status: VideoJobStatus;
    poll_interval_s: number;
  }
  
  export type VideoJobStatus = 
    | 'queued' 
    | 'loading' 
    | 'generating' 
    | 'encoding' 
    | 'done' 
    | 'error';
  
  export interface VideoJobInfo {
    job_id: string;
    status: VideoJobStatus;
    error?: string;
    progress: number;
    video_url?: string;
    fps?: number;
    duration_minutes?: number;
    width?: number;
    height?: number;
  }