export type ArtStyle = 
  | 'Cinematic'
  | 'Photographic'
  | 'Anime'
  | 'Fantasy Art'
  | 'Digital Art'
  | '3D Model'
  | 'Neon Punk'
  | 'Oil Painting'
  | 'Watercolor'
  | 'Freestyle';

export interface QualityPreset {
  steps: number;
  guidance: number;
  label: string;
  time: string;
}

export type QualityLevel = 'fast' | 'balanced' | 'quality' | 'ultra';

export interface ImageGenerationParams {
  prompt: string;
  style: ArtStyle;
  num_inference_steps: number;
  guidance_scale: number;
  width: number;
  height: number;
  negative_prompt?: string;
  seed?: number;
  model_choice?: 'sd3';
}

export interface ImageGenerationResponse {
  success: boolean;
  image_url: string;
  model_used: string;
  width: number;
  height: number;
  num_inference_steps: number;
}