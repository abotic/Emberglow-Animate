import { ArtStyle, QualityLevel, QualityPreset } from "../types/image.types";

export const ART_STYLES: ArtStyle[] = [
  'Cinematic',
  'Photographic',
  'Anime',
  'Fantasy Art',
  'Digital Art',
  '3D Model',
  'Neon Punk',
  'Oil Painting',
  'Watercolor',
  'Freestyle',
];

export const QUALITY_PRESETS: Record<QualityLevel, QualityPreset> = {
  fast: { steps: 25, guidance: 6.0, label: 'Fast', time: '~10s' },
  balanced: { steps: 44, guidance: 7.5, label: 'Balanced', time: '~20s' },
  quality: { steps: 64, guidance: 8.0, label: 'High', time: '~30s' },
  ultra: { steps: 84, guidance: 9.0, label: 'Ultra', time: '~45s' },
};

export const STYLE_PROMPTS: Record<ArtStyle, string> = {
  'Cinematic': 'cinematic lighting, movie still, dramatic atmosphere, film grain, depth of field',
  'Photographic': 'professional photography, DSLR, ultra realistic, sharp focus, high resolution, 8k uhd',
  'Anime': 'anime art style, studio quality, vibrant colors, detailed linework',
  'Fantasy Art': 'fantasy art, magical atmosphere, ethereal lighting, dreamlike quality',
  'Digital Art': 'digital painting, concept art, highly detailed, artstation quality',
  '3D Model': '3d render, octane render, volumetric lighting, ray tracing',
  'Neon Punk': 'cyberpunk, neon lights, futuristic, volumetric fog',
  'Oil Painting': 'oil painting, traditional art, textured brushstrokes, classical style',
  'Watercolor': 'watercolor painting, soft edges, flowing colors, artistic',
  'Freestyle': '',
};

export const DEFAULT_NEGATIVE_PROMPT = 
  'low quality, blurry, distorted, watermark, text, error, messy, bad anatomy, bad hands';