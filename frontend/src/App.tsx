import { useState } from 'react';
import { useWarmup } from './hooks/useWarmup';
import { TabNavigation } from './components/common/TabNavigation';
import { Header } from './components/layout/Header';
import { Footer } from './components/layout/Footer';
import { WarmupBanner } from './components/layout/WarmupBanner';
import { ImageGenerator } from './components/ImageGenerator';
import { VideoGenerator } from './components/VideoGenerator';

export function App() {
  const [activeTab, setActiveTab] = useState<'image' | 'video'>('image');
  const { ready, warming, startWarmup, disabled } = useWarmup();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 text-gray-200">
      <div className="container mx-auto px-4 py-8 md:py-12">
        <Header />
        
        {!ready.all && (
          <WarmupBanner
            ready={ready}
            warming={warming}
            onWarmup={startWarmup}
          />
        )}

        <TabNavigation 
          activeTab={activeTab} 
          onTabChange={setActiveTab} 
        />

        <div className="max-w-4xl mx-auto">
          {activeTab === 'image' ? (
            <ImageGenerator disabled={disabled} />
          ) : (
            <VideoGenerator disabled={disabled} />
          )}
        </div>

        <Footer />
      </div>
    </div>
  );
}