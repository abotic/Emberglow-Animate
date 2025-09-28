export const createImagePreview = (file: File): string => {
    return URL.createObjectURL(file);
  };
  
  export const validateImageFile = (file: File): boolean => {
    return file.type.startsWith('image/');
  };
  
  export const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };