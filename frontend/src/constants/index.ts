export const API_CONFIG = {
    TIMEOUT: 600000, // 10 minutes
    POLL_INTERVAL: 10000, // 10 seconds
    MAX_POLL_RETRIES: 5,
  } as const;
  
  export const DIMENSIONS = {
    DEFAULT_WIDTH: 1024,
    DEFAULT_HEIGHT: 1024,
    MIN_WIDTH: 256,
    MAX_WIDTH: 2048,
    MIN_HEIGHT: 256,
    MAX_HEIGHT: 2048,
  } as const;
  
  export const VIDEO_CONFIG = {
    DEFAULT_BASE_SECONDS: 4,
    MIN_BASE_SECONDS: 2,
    MAX_BASE_SECONDS: 10,
    DEFAULT_FPS: 24,
    MIN_FPS: 8,
    MAX_FPS: 30,
    DEFAULT_DURATION_MINUTES: 30,
    MIN_DURATION: 1,
    MAX_DURATION: 240,
  } as const;