import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { API_CONFIG } from '../constants';

class ApiClient {
  private instance: AxiosInstance;

  constructor() {
    this.instance = axios.create({
      baseURL: '/',
      timeout: API_CONFIG.TIMEOUT,
      validateStatus: (status) => status >= 200 && status < 500,
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    const apiKey = import.meta.env.VITE_API_KEY;

    this.instance.interceptors.request.use((config) => {
      if (apiKey) {
        config.headers.Authorization = `Bearer ${apiKey}`;
      }
      config.headers['Cache-Control'] = 'no-store';
      return config;
    });

    this.instance.interceptors.response.use(
      (response) => {
        if (response.status >= 400) {
          throw new Error(response.data?.detail || 'Request failed');
        }
        return response;
      },
      (error) => {
        throw error;
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.get<T>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.post<T>(url, data, config);
    return response.data;
  }
}

export const apiClient = new ApiClient();