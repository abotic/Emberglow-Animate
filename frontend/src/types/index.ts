export interface ReadyState {
    image: boolean;
    video: boolean;
    all: boolean;
  }
  
  export interface ApiError {
    message: string;
    code?: string;
    details?: Record<string, unknown>;
  }
  
  export type GenerationStatus = 'idle' | 'loading' | 'success' | 'error';