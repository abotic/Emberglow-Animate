export const sleep = (ms: number): Promise<void> => 
    new Promise(resolve => setTimeout(resolve, ms));
  
  export const retry = async <T>(
    fn: () => Promise<T>,
    maxAttempts: number = 3,
    delay: number = 1000
  ): Promise<T> => {
    let lastError: Error | unknown;
    
    for (let i = 0; i < maxAttempts; i++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error;
        if (i < maxAttempts - 1) {
          await sleep(delay);
        }
      }
    }
    
    throw lastError;
  };