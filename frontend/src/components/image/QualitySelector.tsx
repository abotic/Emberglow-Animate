import { Settings } from 'lucide-react';
import { QUALITY_PRESETS } from '@/constants/presets';
import type { QualityLevel } from '@/types/image.types';

interface QualitySelectorProps {
  level: QualityLevel;
  customSettings: { steps: number; guidance: number };
  showAdvanced: boolean;
  onLevelChange: (level: QualityLevel) => void;
  onCustomSettingsChange: (settings: { steps: number; guidance: number }) => void;
  onToggleAdvanced: () => void;
  disabled?: boolean;
}

export function QualitySelector({
  level,
  customSettings,
  showAdvanced,
  onLevelChange,
  onCustomSettingsChange,
  onToggleAdvanced,
  disabled = false,
}: QualitySelectorProps) {
  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <label className="text-sm font-medium text-gray-300">Quality Preset</label>
        <button
          onClick={onToggleAdvanced}
          className="text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1"
          disabled={disabled}
        >
          <Settings size={14} />
          {showAdvanced ? 'Hide' : 'Show'} Advanced
        </button>
      </div>

      {!showAdvanced ? (
        <div className="grid grid-cols-4 gap-2">
          {(Object.entries(QUALITY_PRESETS) as [QualityLevel, typeof QUALITY_PRESETS[QualityLevel]][]).map(
            ([key, preset]) => (
              <button
                key={key}
                onClick={() => {
                  onLevelChange(key);
                  onCustomSettingsChange({ steps: preset.steps, guidance: preset.guidance });
                }}
                className={`p-2 rounded-lg text-sm transition-all ${
                  level === key
                    ? 'bg-purple-500/30 border border-purple-500 text-white'
                    : 'bg-gray-700/50 border border-gray-600 text-gray-300 hover:border-gray-500'
                }`}
                disabled={disabled}
              >
                <div className="font-medium">{preset.label}</div>
                <div className="text-xs text-gray-400">{preset.time}</div>
              </button>
            )
          )}
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 p-4 bg-gray-700/30 rounded-lg">
          <div>
            <label className="text-xs text-gray-400">Steps ({customSettings.steps})</label>
            <input
              type="range"
              min="20"
              max="150"
              value={customSettings.steps}
              onChange={(e) =>
                onCustomSettingsChange({ ...customSettings, steps: Number(e.target.value) })
              }
              className="w-full mt-1"
              disabled={disabled}
            />
          </div>
          <div>
            <label className="text-xs text-gray-400">Guidance ({customSettings.guidance})</label>
            <input
              type="range"
              min="1"
              max="15"
              step="0.5"
              value={customSettings.guidance}
              onChange={(e) =>
                onCustomSettingsChange({ ...customSettings, guidance: Number(e.target.value) })
              }
              className="w-full mt-1"
              disabled={disabled}
            />
          </div>
        </div>
      )}
    </div>
  );
}