import { AlertCircle } from 'lucide-react';

interface ErrorMessageProps {
  message: string;
  className?: string;
}

export function ErrorMessage({ message, className = '' }: ErrorMessageProps) {
  return (
    <div className={`bg-red-900/50 border border-red-500 text-red-300 px-4 py-3 rounded-lg text-sm flex items-start gap-2 ${className}`}>
      <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
      <div>
        <span className="font-semibold">Error:</span> {message}
      </div>
    </div>
  );
}