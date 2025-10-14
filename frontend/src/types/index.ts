export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, unknown>;
}

export type GenerationStatus = 'idle' | 'loading' | 'success' | 'error';