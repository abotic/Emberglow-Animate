interface WarmupBannerProps {
  ready: boolean;
  warming: boolean;
  onWarmup: () => void;
}

export function WarmupBanner({ ready, warming, onWarmup }: WarmupBannerProps) {
  return (
    <div className="max-w-3xl mx-auto mb-6 p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/40 text-yellow-200 text-sm flex items-center justify-between">
      <div>
        <strong>Warming up model…</strong> This is only needed after a restart.
        <div className="text-xs opacity-80 mt-1">
          Model ready: {ready ? 'Yes' : 'Loading...'}
        </div>
      </div>
      <button
        onClick={onWarmup}
        disabled={warming}
        className={`px-3 py-1.5 rounded-md border ${
          warming ? 'opacity-50 cursor-not-allowed' : 'hover:bg-yellow-500/20'
        } border-yellow-500/60`}
      >
        {warming ? 'Starting…' : 'Warm up now'}
      </button>
    </div>
  );
}