import React, { useCallback } from 'react';
import { UploadCloud, X } from 'lucide-react';
import { createImagePreview, validateImageFile } from '@/utils/file.utils';

interface ImageUploaderProps {
  file: File | null;
  onChange: (file: File | null) => void;
  disabled?: boolean;
}

export function ImageUploader({ file, onChange, disabled = false }: ImageUploaderProps) {
  const preview = file ? createImagePreview(file) : null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile && validateImageFile(selectedFile)) {
      onChange(selectedFile);
    }
  };

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile && validateImageFile(droppedFile)) {
        onChange(droppedFile);
      }
    },
    [onChange]
  );

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const clearFile = () => {
    onChange(null);
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-300 mb-2">
        Upload Image to Animate
      </label>
      <div
        className={`relative w-full h-64 border-2 border-dashed rounded-lg flex items-center justify-center text-center transition-colors ${
          preview ? 'border-purple-500 bg-gray-900/50' : 'border-gray-600 hover:border-gray-500'
        }`}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        {preview ? (
          <>
            <img 
              src={preview} 
              alt="Preview" 
              className="max-h-full max-w-full rounded-md object-contain" 
            />
            <button
              onClick={clearFile}
              className="absolute top-2 right-2 bg-gray-900/70 p-1.5 rounded-full text-gray-300 hover:text-white hover:bg-gray-800 transition-all"
              disabled={disabled}
            >
              <X size={18} />
            </button>
          </>
        ) : (
          <div className="text-gray-400">
            <UploadCloud size={48} className="mx-auto mb-2" />
            <p className="font-semibold">Drag & drop an image here</p>
            <p className="text-sm mt-1">or</p>
            <label
              htmlFor="file-upload"
              className="font-medium text-purple-400 hover:text-purple-300 cursor-pointer"
            >
              Click to browse
            </label>
            <input
              id="file-upload"
              type="file"
              className="sr-only"
              accept="image/*"
              onChange={handleFileChange}
              disabled={disabled}
            />
          </div>
        )}
      </div>
    </div>
  );
}