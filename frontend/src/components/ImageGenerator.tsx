import { useState } from 'react';
import { Sparkles } from 'lucide-react';
import { DIMENSIONS } from '@/constants';
import { Button } from './common/Button';
import { useImageGenerator } from '@/hooks/useImageGenerator';
import { ArtStyle, QualityLevel } from '@/types/image.types';
import { ErrorMessage } from './common/ErrorMessage';
import { GeneratedImageDisplay } from './image/GeneratedImageDisplay';
import { QualitySelector } from './image/QualitySelector';
import { StyleSelector } from './image/StyleSelector';

interface ImageGeneratorProps {
  disabled?: boolean;
}

export function ImageGenerator({ disabled = false }: ImageGeneratorProps) {
  const [prompt, setPrompt] = useState('A cozy cabin at night, warm fireplace glow through window, snow outside');
  const [style, setStyle] = useState<ArtStyle>('Cinematic');
  const [qualityLevel, setQualityLevel] = useState<QualityLevel>('balanced');
  const [customSettings, setCustomSettings] = useState({ steps: 44, guidance: 7.5 });
  const [showAdvanced, setShowAdvanced] = useState(false);

  const { generate, result, error, isLoading } = useImageGenerator();

  const handleGenerate = () => {
    if (!prompt.trim()) return;
    
    generate({
      prompt,
      style,
      num_inference_steps: customSettings.steps,
      guidance_scale: customSettings.guidance,
      width: DIMENSIONS.DEFAULT_WIDTH,
      height: DIMENSIONS.DEFAULT_HEIGHT,
    });
  };

  return (
    <div className="bg-gray-800/50 rounded-xl shadow-2xl p-6 md:p-8 border border-gray-700">
      {disabled && (
        <div className="mb-4 text-sm text-yellow-300">
          Models are warming up… generation is temporarily disabled.
        </div>
      )}

      <div className="space-y-6">
        <QualitySelector
          level={qualityLevel}
          customSettings={customSettings}
          showAdvanced={showAdvanced}
          onLevelChange={setQualityLevel}
          onCustomSettingsChange={setCustomSettings}
          onToggleAdvanced={() => setShowAdvanced(!showAdvanced)}
          disabled={disabled || isLoading}
        />

        <StyleSelector
          value={style}
          onChange={setStyle}
          disabled={disabled || isLoading}
        />

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Enter your prompt
          </label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="w-full h-28 px-4 py-3 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-purple-500 focus:ring-2 focus:ring-purple-500 focus:outline-none transition-all resize-none"
            disabled={disabled || isLoading}
          />
        </div>

        <Button
          onClick={handleGenerate}
          disabled={disabled || !prompt.trim()}
          loading={isLoading}
          icon={<Sparkles className="h-5 w-5" />}
          fullWidth
        >
          {isLoading ? 'Generating…' : 'Generate Image'}
        </Button>

        {error && <ErrorMessage message={error} />}
        {result && <GeneratedImageDisplay imageUrl={result.image_url} />}
      </div>
    </div>
  );
}