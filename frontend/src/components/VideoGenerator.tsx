import { useState } from 'react';
import { Film } from 'lucide-react';
import { VIDEO_CONFIG } from '@/constants';
import { VideoGenerationOptions } from '@/types/video.types';
import { Button } from './common/Button';
import { useVideoGenerator } from '@/hooks/useVideoGenerator';
import { ErrorMessage } from './common/ErrorMessage';
import { GeneratedVideoDisplay } from './video/GeneratedVideoDisplay';
import { ImageUploader } from './video/ImageUploader';
import { VideoOptions } from './video/VideoOptions';

interface VideoGeneratorProps {
  disabled?: boolean;
}

export function VideoGenerator({ disabled = false }: VideoGeneratorProps) {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [options, setOptions] = useState<VideoGenerationOptions>({
    video_type: 'ambient_loop',
    enhance_quality: true,
    create_loop: true,
    base_seconds: VIDEO_CONFIG.DEFAULT_BASE_SECONDS,
    fps: VIDEO_CONFIG.DEFAULT_FPS,
    duration_minutes: VIDEO_CONFIG.DEFAULT_DURATION_MINUTES,
  });

  const { generate, result, error, isLoading, statusText } = useVideoGenerator();

  const handleGenerate = () => {
    if (!imageFile) return;
    generate(imageFile, options);
  };

  return (
    <div className="bg-gray-800/50 rounded-xl shadow-2xl p-6 md:p-8 border border-gray-700">
      {disabled && (
        <div className="mb-4 text-sm text-yellow-300">
          Models are warming up… generation is temporarily disabled.
        </div>
      )}

      <div className="space-y-6">
        <VideoOptions
          options={options}
          onChange={setOptions}
          disabled={disabled || isLoading}
        />

        <ImageUploader
          file={imageFile}
          onChange={setImageFile}
          disabled={disabled || isLoading}
        />

        <Button
          onClick={handleGenerate}
          disabled={disabled || !imageFile}
          loading={isLoading}
          icon={<Film className="h-5 w-5" />}
          fullWidth
        >
          {isLoading && statusText ? `Processing: ${statusText}` : 'Generate Loop'}
        </Button>

        {error && <ErrorMessage message={error} />}
        {result && <GeneratedVideoDisplay video={result} />}
      </div>
    </div>
  );
}