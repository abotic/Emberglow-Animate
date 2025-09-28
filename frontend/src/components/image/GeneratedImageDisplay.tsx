import { Download } from 'lucide-react';

interface GeneratedImageDisplayProps {
  imageUrl: string;
}

export function GeneratedImageDisplay({ imageUrl }: GeneratedImageDisplayProps) {
  return (
    <div className="border-t border-gray-700 pt-6">
      <h3 className="text-lg font-medium text-gray-200 mb-4">Generated Image</h3>
      <div className="relative group rounded-lg overflow-hidden">
        <img 
          src={imageUrl} 
          alt="Generated" 
          className="w-full h-auto bg-gray-900" 
        />
        <a
          href={imageUrl}
          download="generated-image.png"
          className="absolute top-4 right-4 bg-black/60 backdrop-blur-sm text-white px-4 py-2 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300 text-sm hover:bg-black/80 flex items-center gap-2"
        >
          <Download size={16} />
          Download
        </a>
      </div>
    </div>
  );
}