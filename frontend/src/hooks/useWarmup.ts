import { useEffect, useRef, useState } from 'react';
import { apiClient } from '@/services/api.client';
import { API_CONFIG } from '@/constants';

interface ApiReadyResponse {
  ready: boolean;
}

export function useWarmup() {
  const [ready, setReady] = useState(false);
  const [videoEnabled, setVideoEnabled] = useState(false);
  const [warming, setWarming] = useState(false);
  const pollIntervalRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    const checkReady = async () => {
      try {
        const response = await apiClient.get<ApiReadyResponse>('/api/ready');
        setReady(response.ready);
        
        if (response.ready && pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = undefined;
        }
      } catch (error) {
        console.error('Failed to check ready status:', error);
      }
    };

    const checkVideo = async () => {
      try {
        await apiClient.get('/api/video/job/test');
        setVideoEnabled(true);
      } catch {
        setVideoEnabled(false);
      }
    };

    checkReady();
    checkVideo();
    pollIntervalRef.current = setInterval(checkReady, API_CONFIG.POLL_INTERVAL);

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  const startWarmup = async () => {
    try {
      setWarming(true);
      await apiClient.post('/api/warmup');
    } finally {
      setTimeout(() => setWarming(false), 1500);
    }
  };

  return {
    ready,
    videoEnabled,
    warming,
    startWarmup,
    disabled: !ready || warming,
  };
}