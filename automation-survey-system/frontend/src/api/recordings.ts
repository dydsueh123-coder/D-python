import apiClient from './client'
import type { Recording } from '../types/recording'

export const recordingsApi = {
  list: () =>
    apiClient.get<Recording[]>('/recordings'),

  upload: (formData: FormData, onProgress?: (pct: number) => void) =>
    apiClient.post<Recording>('/recordings/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress && e.total) {
          onProgress(Math.round((e.loaded * 100) / e.total))
        }
      },
    }),
}
