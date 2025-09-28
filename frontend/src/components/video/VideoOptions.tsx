import { Palette, Zap } from 'lucide-react';
import { VIDEO_CONFIG } from '@/constants';
import type { VideoGenerationOptions } from '@/types/video.types';

interface VideoOptionsProps {
  options: VideoGenerationOptions;
  onChange: (options: VideoGenerationOptions) => void;
  disabled?: boolean;
}

export function VideoOptions({ options, onChange, disabled = false }: VideoOptionsProps) {
  const updateOption = <K extends keyof VideoGenerationOptions>(
    key: K,
    value: VideoGenerationOptions[K]
  ) => {
    onChange({ ...options, [key]: value });
  };

  return (
    <>
      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="block text-xs text-gray-400 mb-1">Base seconds</label>
          <input
            type="number"
            min={VIDEO_CONFIG.MIN_BASE_SECONDS}
            max={VIDEO_CONFIG.MAX_BASE_SECONDS}
            value={options.base_seconds}
            onChange={(e) => updateOption('base_seconds', Number(e.target.value))}
            className="w-full px-3 py-2 rounded bg-gray-700 border border-gray-600 text-white focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
            disabled={disabled}
          />
        </div>
        <div>
          <label className="block text-xs text-gray-400 mb-1">FPS</label>
          <input
            type="number"
            min={VIDEO_CONFIG.MIN_FPS}
            max={VIDEO_CONFIG.MAX_FPS}
            value={options.fps}
            onChange={(e) => updateOption('fps', Number(e.target.value))}
            className="w-full px-3 py-2 rounded bg-gray-700 border border-gray-600 text-white focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
            disabled={disabled}
          />
        </div>
        <div>
          <label className="block text-xs text-gray-400 mb-1">Duration (min)</label>
          <input
            type="number"
            min={VIDEO_CONFIG.MIN_DURATION}
            max={VIDEO_CONFIG.MAX_DURATION}
            value={options.duration_minutes}
            onChange={(e) => updateOption('duration_minutes', Number(e.target.value))}
            className="w-full px-3 py-2 rounded bg-gray-700 border border-gray-600 text-white focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
            disabled={disabled}
          />
        </div>
      </div>

      <div className="space-y-3 p-4 bg-gray-700/30 rounded-lg">
        <label className="flex items-center space-x-3">
          <input
            type="checkbox"
            checked={options.enhance_quality}
            onChange={(e) => updateOption('enhance_quality', e.target.checked)}
            className="w-4 h-4 text-purple-500 bg-gray-700 rounded focus:ring-purple-500"
            disabled={disabled}
          />
          <span className="text-sm text-gray-300">
            <Palette className="inline w-4 h-4 mr-1" />
            Enhance quality (reduces blur)
          </span>
        </label>
        <label className="flex items-center space-x-3">
          <input
            type="checkbox"
            checked={options.create_loop}
            onChange={(e) => updateOption('create_loop', e.target.checked)}
            className="w-4 h-4 text-purple-500 bg-gray-700 rounded focus:ring-purple-500"
            disabled={disabled}
          />
          <span className="text-sm text-gray-300">
            <Zap className="inline w-4 h-4 mr-1" />
            Make seamless loop
          </span>
        </label>
      </div>
    </>
  );
}