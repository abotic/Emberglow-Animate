import { ART_STYLES } from '@/constants/presets';
import type { ArtStyle } from '@/types/image.types';

interface StyleSelectorProps {
  value: ArtStyle;
  onChange: (style: ArtStyle) => void;
  disabled?: boolean;
}

export function StyleSelector({ value, onChange, disabled = false }: StyleSelectorProps) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-300 mb-2">Art Style</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as ArtStyle)}
        className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-purple-500 focus:ring-2 focus:ring-purple-500 focus:outline-none transition-all"
        disabled={disabled}
      >
        {ART_STYLES.map((style) => (
          <option key={style} value={style}>
            {style}
          </option>
        ))}
      </select>
    </div>
  );
}