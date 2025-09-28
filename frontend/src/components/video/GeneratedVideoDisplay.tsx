import { Download } from 'lucide-react';
import type { VideoJobInfo } from '@/types/video.types';

interface GeneratedVideoDisplayProps {
  video: VideoJobInfo;
}

export function GeneratedVideoDisplay({ video }: GeneratedVideoDisplayProps) {
  if (!video.video_url) return null;

  return (
    <div className="border-t border-gray-700 pt-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-200">Generated Video</h3>
        <span className="text-sm text-gray-400">
          {video.duration_minutes ?? 30} min • {video.fps ?? 24} fps
        </span>
      </div>
      <div className="relative group rounded-lg overflow-hidden bg-black">
        <video 
          src={video.video_url} 
          controls 
          autoPlay 
          loop 
          muted 
          className="w-full h-auto"
        />
        <a
          href={video.video_url}
          download="generated-video.mp4"
          className="absolute top-4 right-4 bg-black/60 backdrop-blur-sm text-white px-4 py-2 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300 text-sm hover:bg-black/80 flex items-center gap-2"
        >
          <Download size={16} />
          Download
        </a>
      </div>
    </div>
  );
}