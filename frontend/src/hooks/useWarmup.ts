import { useEffect, useRef, useState } from 'react';
import { apiClient } from '@/services/api.client';
import type { ReadyState } from '@/types';
import { API_CONFIG } from '@/constants';

interface ApiReadyResponse {
  ready: ReadyState;
}

export function useWarmup() {
  const [ready, setReady] = useState<ReadyState>({
    image: false,
    video: false,
    all: false,
  });
  const [warming, setWarming] = useState(false);
  const pollIntervalRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    const checkReady = async () => {
      try {
        const response = await apiClient.get<ApiReadyResponse>('/api/ready');
        setReady(response.ready);
        
        if (response.ready.all && pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = undefined;
        }
      } catch (error) {
        console.error('Failed to check ready status:', error);
      }
    };

    checkReady();
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
    warming,
    startWarmup,
    disabled: !ready.all || warming,
  };
}