import { useState } from 'react';
import { imageService } from '@/services/image.service';
import { STYLE_PROMPTS, DEFAULT_NEGATIVE_PROMPT } from '@/constants/presets';
import { GenerationStatus } from '@/types';
import { ImageGenerationResponse, ImageGenerationParams } from '@/types/image.types';

export function useImageGenerator() {
  const [status, setStatus] = useState<GenerationStatus>('idle');
  const [result, setResult] = useState<ImageGenerationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const generate = async (params: ImageGenerationParams) => {
    setStatus('loading');
    setError(null);
    setResult(null);

    try {
      const stylePrompt = STYLE_PROMPTS[params.style] || '';
      const enhancedPrompt = stylePrompt 
        ? `${params.prompt}, ${stylePrompt}, masterpiece, best quality`
        : params.prompt;

      const response = await imageService.generate({
        ...params,
        prompt: enhancedPrompt,
        negative_prompt: params.negative_prompt || DEFAULT_NEGATIVE_PROMPT,
      });

      setResult(response);
      setStatus('success');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate image');
      setStatus('error');
    }
  };

  return {
    generate,
    status,
    result,
    error,
    isLoading: status === 'loading',
  };
}